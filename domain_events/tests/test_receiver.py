from domain_events import Receiver, Retry, DEFAULT_CONNECTION_SETTINGS, send_domain_event
from .helpers import (
    check_queue_exists, get_message_from_queue, get_queue_size,
    )
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
    receiver = Receiver(DEFAULT_CONNECTION_SETTINGS)
    receiver.register(raise_retry, name, ['test.retry'], max_retries=3)
    data = dict(message=str(uuid.uuid4())[:4])
    send_domain_event(DEFAULT_CONNECTION_SETTINGS, 'test.retry', data)
    receiver.start_consuming(timeout=1.0)
    assert raise_retry.received == 4
    assert get_queue_size(name) == 0


def test_auto_delete():
    name = 'test-auto-delete'
    receiver = Receiver(DEFAULT_CONNECTION_SETTINGS)
    receiver.register(nop, name, ['test.auto_delete'], auto_delete=True)
    send_domain_event(DEFAULT_CONNECTION_SETTINGS, 'test.auto_delete', {})
    receiver.start_consuming(timeout=1.0)
    assert not check_queue_exists(name)


def test_multiple_listeneres():
    def one(event):
        one.received += 1
    one.received = 0

    def two(event):
        two.received += 1
    two.received = 0

    receiver = Receiver(DEFAULT_CONNECTION_SETTINGS)
    receiver.register(one, 'test-listener-one', ['test.one'])
    receiver.register(two, 'test-listener-two', ['test.two'])
    send_domain_event(DEFAULT_CONNECTION_SETTINGS, 'test.one', {})
    send_domain_event(DEFAULT_CONNECTION_SETTINGS, 'test.two', {})
    receiver.start_consuming(timeout=1.0)
    assert one.received == 1
    assert two.received == 1


def test_consumer_timeout():
    name = 'test-consumer-timeout'
    receiver = Receiver(DEFAULT_CONNECTION_SETTINGS)
    receiver.register(nop, name, ['#'])
    receiver.start_consuming(timeout=1.0)


def test_dead_letter():
    name = 'test-dead-letter'
    receiver = Receiver(DEFAULT_CONNECTION_SETTINGS)
    receiver.register(raise_error, name, ['test.dl'], dead_letter=True)
    data = dict(message=str(uuid.uuid4())[:4])
    send_domain_event(DEFAULT_CONNECTION_SETTINGS, 'test.dl', data)
    with pytest.raises(ConsumerError):
        receiver.start_consuming(timeout=1.0)
    header, event = get_message_from_queue('test-dead-letter-dl')
    assert event.data == data
