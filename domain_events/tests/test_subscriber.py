from domain_events import Subscriber, Retry, publish_domain_event
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
    subscriber = Subscriber()
    subscriber.register(raise_retry, name, ['test.retry'], max_retries=3)
    data = dict(message=str(uuid.uuid4())[:4])
    publish_domain_event('test.retry', data)
    subscriber.start_consuming(timeout=1.0)
    assert raise_retry.received == 4
    assert get_queue_size(name) == 0


def test_auto_delete():
    name = 'test-auto-delete'
    subscriber = Subscriber()
    subscriber.register(nop, name, ['test.auto_delete'], auto_delete=True)
    publish_domain_event('test.auto_delete', {})
    subscriber.start_consuming(timeout=1.0)
    assert not check_queue_exists(name)


def test_multiple_listeneres():
    def one(event):
        one.received += 1
    one.received = 0

    def two(event):
        two.received += 1
    two.received = 0

    subscriber = Subscriber()
    subscriber.register(one, 'test-listener-one', ['test.one'])
    subscriber.register(two, 'test-listener-two', ['test.two'])
    publish_domain_event('test.one', {})
    publish_domain_event('test.two', {})
    subscriber.start_consuming(timeout=1.0)
    assert one.received == 1
    assert two.received == 1


def test_consumer_timeout():
    name = 'test-consumer-timeout'
    subscriber = Subscriber()
    subscriber.register(nop, name, ['#'])
    subscriber.start_consuming(timeout=1.0)


def test_dead_letter():
    name = 'test-dead-letter'
    subscriber = Subscriber()
    subscriber.register(raise_error, name, ['test.dl'], dead_letter=True)
    data = dict(message=str(uuid.uuid4())[:4])
    publish_domain_event('test.dl', data)
    with pytest.raises(ConsumerError):
        subscriber.start_consuming(timeout=1.0)
    header, event = get_message_from_queue('test-dead-letter-dl')
    assert event.data == data
