import json

from domain_events import (
    configure,
    emit_domain_event,
    DomainEvent,
    )

configure()

from domain_events.rabbitmq_transport import default_transport as transport


class TestEvent(object):

    def test_fire_event(self):
        """Use basic API to fire event"""
        event = DomainEvent.create_and_fire('test.test', {})
        json_data, routing_key = transport.messages[-1]
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_event_loading(self):
        event = emit_domain_event('test.test', {})
        json_data, routing_key = transport.messages[-1]

        new_event = DomainEvent.from_json(json_data)
        assert new_event == event
