from domain_event_broker import publish_domain_event, Subscriber
from .helpers import check_queue_exists, get_queue_size
import uuid


def test_publish():
    def handle_event(event):
        handle_event.message = event.data['message']
    handle_event.message = None
    name = 'test-publish'
    subscriber = Subscriber()
    subscriber.register(handle_event, name, ['test.publish'])
    data = dict(message=str(uuid.uuid4())[:4])
    publish_domain_event('test.publish', data)
    subscriber.start_consuming(timeout=1.0)
    assert handle_event.message == data['message']
    assert get_queue_size(name) == 0


def test_dummy_mode():
    def handle_event(event):
        handle_event.message = event.data['message']
    handle_event.message = None
    name = 'test-dummy'
    subscriber = Subscriber(connection_settings=None)
    subscriber.register(handle_event, name, ['test.publish-dummy'])
    publish_domain_event('test.publish-dummy', {}, connection_settings=None)
    subscriber.start_consuming(timeout=1.0)
    assert not check_queue_exists(name)
