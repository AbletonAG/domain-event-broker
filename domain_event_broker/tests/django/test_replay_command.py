from django.core.management import call_command
from ..helpers import get_message_from_queue, get_queue_size


def test_replay(dead_letter_message):
    call_command('replay_domain_event', 'test-replay')
    assert get_queue_size('test-replay-dl') == 0
    header, event = get_message_from_queue('test-replay')
    assert event.data == dead_letter_message
