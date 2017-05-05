from domain_events import replay
from .helpers import get_message_from_queue, get_queue_size


def test_replay(dead_letter_message):
    assert replay.replay('test-replay') == 0
    assert get_queue_size('test-replay-dl') == 0
    header, event = get_message_from_queue('test-replay')
    assert event.data == dead_letter_message


def discard(**kwargs):
    return replay.DISCARD


def test_discard(dead_letter_message):
    assert replay.replay('test-replay', message_callback=discard) == 0
    assert get_queue_size('test-replay-dl') == 0
    assert get_queue_size('test-replay') == 0


def leave(**kwargs):
    return replay.LEAVE


def test_leave(dead_letter_message):
    assert replay.replay('test-replay', message_callback=leave) == 0
    assert get_queue_size('test-replay-dl') == 1
    assert get_queue_size('test-replay') == 0
    header, event = get_message_from_queue('test-replay-dl')
    assert event.data == dead_letter_message
