from domain_events import replay
from domain_events import emit_domain_event, Receiver, transmit
from .helpers import get_message_from_queue, get_queue_size
import pytest
import uuid


class ConsumerError(Exception):
    pass


def raise_error(event):
    raise ConsumerError("Unexpected error")


def dead_letter_message():
    name = 'test-replay'
    receiver = Receiver()
    receiver.register(raise_error, name, ['test.replay'], dead_letter=True)
    data = dict(message=str(uuid.uuid4())[:4])
    emit_domain_event('test.replay', data)
    transmit()
    with pytest.raises(ConsumerError):
        receiver.start_consuming(timeout=1.0)
    return data


def test_replay():
    data = dead_letter_message()
    assert replay.replay('test-replay') == 0
    assert get_queue_size('test-replay-dl') == 0
    header, event = get_message_from_queue('test-replay')
    assert event.data == data


def discard(**kwargs):
    return replay.DISCARD


def test_discard():
    dead_letter_message()
    assert replay.replay('test-replay', message_callback=discard) == 0
    assert get_queue_size('test-replay-dl') == 0
    assert get_queue_size('test-replay') == 0


def leave(**kwargs):
    return replay.LEAVE


def test_leave():
    message = dead_letter_message()
    assert replay.replay('test-replay', message_callback=leave) == 0
    assert get_queue_size('test-replay-dl') == 1
    assert get_queue_size('test-replay') == 0
    header, event = get_message_from_queue('test-replay-dl')
    assert event.data == message
