import json

from domain_events import (
    send_domain_event,
    DomainEvent,
    )

from domain_events.transport import get_sender


class TestEvent(object):

    def test_fire_event(self):
        """Use basic API to fire event"""
        event = send_domain_event('test.test', {})
        json_data, routing_key = get_sender().messages[-1]
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_event_loading(self):
        event = send_domain_event('test.test', {})
        json_data, routing_key = get_sender().messages[-1]

        new_event = DomainEvent.from_json(json_data)
        assert new_event == event
