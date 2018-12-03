from django.core.management.base import BaseCommand

from domain_event_broker import replay


class Command(BaseCommand):

    help = "Move dead-lettered event back into given subscriber queue"

    def add_arguments(self, parser):
        parser.add_argument('queue', nargs='+', type=str)
        parser.add_argument(
            '--all',
            action='store_true',
            dest='replay_all',
            default=False,
            help='Replay all events in dead letter queue.',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            dest='interactive',
            default=False,
            help='Ask for desired action for each event.',
        )

    def interactive_filter(self, body=None, **kwargs):
        self.stdout.write("Please specify action for: '{}'".format(body))
        action = input("(R)eplay, (D)iscard or (L)eave? ")[0].upper()
        return {
            'R': replay.RETRY,
            'D': replay.DISCARD,
            'L': replay.LEAVE,
            }[action]

    def handle(self, *args, **options):
        callback = replay.retry_event
        if options['interactive']:
            callback = self.interactive_filter
        for queue in options['queue']:
            if options['replay_all']:
                remaining = replay.replay_all(queue, callback)
            else:
                remaining = replay.replay_event(queue, callback)
            self.stdout.write("{} dead-lettered events remaining for {}".format(remaining, queue))
