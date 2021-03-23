import json
import select
import sys

from typing import Any, Optional
from django.core.management.base import BaseCommand

from argparse import ArgumentParser
from domain_event_broker import replay


def input_timeout(timeout: int) -> Optional[str]:
    inp, _, _ = select.select([sys.stdin], [], [], timeout)
    return sys.stdin.readline().strip() if inp else None


class Command(BaseCommand):

    help = "Move dead-lettered event back into given subscriber queue"

    def add_arguments(self, parser: ArgumentParser) -> None:
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

    def interactive_filter(self, body: bytes, **kwargs: Any) -> str:
        payload = json.loads(body)
        self.stdout.write("Please specify action for:")
        self.stdout.write(json.dumps(payload, indent=4, sort_keys=True))
        self.stdout.write("(R)eplay, (D)iscard or (L)eave?")
        # Wait for user input but time out before the RabbitMQ connection is
        # lost.
        action = input_timeout(30)
        if action is None:
            self.stdout.write("Timed out. Message left in queue.")
            return replay.LEAVE
        elif action == '':
            self.stdout.write("Message left in queue.")
            return replay.LEAVE
        action = action[0].upper()
        if action == 'R':
            self.stdout.write("Message is returned to worker queue.")
            return replay.RETRY
        elif action == 'D':
            self.stdout.write("Message has been discarded.")
            return replay.DISCARD
        else:
            self.stdout.write("Message left in queue.")
            return replay.LEAVE

    def handle(self, *args: Any, **options: Any) -> None:
        callback = replay.retry_event
        if options['interactive']:
            callback = self.interactive_filter
        for queue in options['queue']:
            if options['replay_all']:
                remaining = replay.replay_all(queue, callback)
            else:
                remaining = replay.replay_event(queue, callback)
            self.stdout.write("{} dead-lettered events remaining for {}".format(remaining, queue))
