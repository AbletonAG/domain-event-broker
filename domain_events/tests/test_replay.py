from domain_events import replay, publish_domain_event, Subscriber
from .helpers import get_message_from_queue, get_queue_size
import pytest
import uuid


class ConsumerError(Exception):
    pass


def raise_error(event):
    raise ConsumerError("Unexpected error")


@pytest.fixture
def dead_letter_message():
    name = 'test-replay'
    subscriber = Subscriber()
    subscriber.register(raise_error, name, ['test.replay'], dead_letter=True)
    data = dict(message=str(uuid.uuid4())[:4])
    publish_domain_event('test.replay', data)
    with pytest.raises(ConsumerError):
        subscriber.start_consuming(timeout=1.0)
    yield data
    transport = Subscriber()
    transport.channel.queue_delete(queue='test-replay')
    transport.channel.queue_delete(queue='test-replay-dl')


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
