from domain_event_broker import publish_domain_event, Subscriber
from .helpers import delete_queue
import pytest
import uuid


class ConsumerError(Exception):
    pass


def raise_error(event):
    raise ConsumerError("Unexpected error")


@pytest.fixture
def dead_letter_message():
    name = 'test-replay'
    delete_queue(name)
    subscriber = Subscriber()
    subscriber.register(raise_error, name, ['test.replay'], dead_letter=True)
    data = dict(message=str(uuid.uuid4())[:4])
    publish_domain_event('test.replay', data)
    subscriber.start_consuming(timeout=0.5)
    yield data
    transport = Subscriber()
    transport.channel.queue_delete(queue='test-replay')
    transport.channel.queue_delete(queue='test-replay-dl')
