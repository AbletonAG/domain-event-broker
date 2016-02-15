import json
import pytest
from tests.test_queues import get_queue
from domain_events.events import DomainEvent, fire_domain_event

class TestEvent(object):

    def setup(self):
        self.transport = get_queue(False)

    def test_dummy(self):
        event = DomainEvent('test', 'test', {})
        fire_domain_event(event, self.transport)
        event_data, routing_key = self.transport.last_message
        event_data = json.loads(event_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid'] == event.uuid
