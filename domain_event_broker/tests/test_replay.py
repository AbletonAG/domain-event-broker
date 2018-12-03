from domain_event_broker import replay_event, Subscriber, DISCARD, LEAVE
from .helpers import get_message_from_queue, get_queue_size


def test_replay(dead_letter_message):
    assert replay_event('test-replay') == 0
    assert get_queue_size('test-replay-dl') == 0
    header, event = get_message_from_queue('test-replay')
    assert event.data == dead_letter_message


def discard(**kwargs):
    return DISCARD


def test_discard(dead_letter_message):
    assert replay_event('test-replay', message_callback=discard) == 0
    assert get_queue_size('test-replay-dl') == 0
    assert get_queue_size('test-replay') == 0


def leave(**kwargs):
    return LEAVE


def test_leave(dead_letter_message):
    assert replay_event('test-replay', message_callback=leave) == 0
    assert get_queue_size('test-replay-dl') == 1
    assert get_queue_size('test-replay') == 0
    header, event = get_message_from_queue('test-replay-dl')
    assert event.data == dead_letter_message


def nop(event):
    pass


def test_empty_queue():
    name = 'test-empty-queue'
    subscriber = Subscriber()
    subscriber.register(nop, name, ['test.empty'], dead_letter=True)
    assert replay_event('test-empty-queue') == 0
