from domain_events import emit_domain_event, Receiver, Retry, transmit
from .helpers import check_queue_exists, get_message_from_queue, get_queue_size
import pytest
import uuid


def nop(event):
    pass


class ConsumerError(Exception):
    pass


def raise_error(event):
    raise ConsumerError("Unexpected error")


def test_retry():
    def raise_retry(event):
        raise_retry.received += 1
        raise Retry(0.1)
    raise_retry.received = 0

    name = 'test-retry'
    receiver = Receiver()
    receiver.register(raise_retry, name, ['test.retry'], max_retries=3)
    data = dict(message=str(uuid.uuid4())[:4])
    emit_domain_event('test.retry', data)
    transmit()
    receiver.start_consuming(timeout=1.0)
    assert raise_retry.received == 4
    assert get_queue_size(name) == 0


def test_auto_delete():
    name = 'test-auto-delete'
    receiver = Receiver()
    receiver.register(nop, name, ['test.auto_delete'], auto_delete=True)
    emit_domain_event('test.auto_delete', {})
    transmit()
    receiver.start_consuming(timeout=1.0)
    assert not check_queue_exists(name)


def test_multiple_listeneres():
    def one(event):
        one.received += 1
    one.received = 0

    def two(event):
        two.received += 1
    two.received = 0

    receiver = Receiver()
    receiver.register(one, 'test-listener-one', ['test.one'])
    receiver.register(two, 'test-listener-two', ['test.two'])
    emit_domain_event('test.one', {})
    emit_domain_event('test.two', {})
    transmit()
    receiver.start_consuming(timeout=1.0)
    assert one.received == 1
    assert two.received == 1


def test_maximum_number_of_messages():
    def one(event):
        one.received += 1
    one.received = 0

    def two(event):
        two.received += 1
    two.received = 0

    receiver = Receiver(max_messages=1)
    receiver.register(one, 'test-max-listener-one', ['test.max.one'])
    receiver.register(two, 'test-max-listener-two', ['test.max.two'])
    emit_domain_event('test.max.one', {})
    emit_domain_event('test.max.two', {})
    transmit()
    receiver.start_consuming(timeout=1.0)
    assert (one.received + two.received) == 1


def xtest_consumer_timeout():
    receiver = Receiver()
    receiver.register(nop, 'test-consumer-timeout', ['#'])
    receiver.start_consuming(timeout=1.0)


def test_dead_letter():
    name = 'test-dead-letter'
    receiver = Receiver()
    receiver.register(raise_error, name, ['test.dl'], dead_letter=True)
    data = dict(message=str(uuid.uuid4())[:4])
    emit_domain_event('test.dl', data)
    transmit()
    with pytest.raises(ConsumerError):
        receiver.start_consuming(timeout=1.0)
    header, event = get_message_from_queue('test-dead-letter-dl')
    assert event.data == data
