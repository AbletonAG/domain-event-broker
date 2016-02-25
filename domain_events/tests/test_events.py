import json

from domain_events import (
    emit_domain_event,
    flush,
    DomainEvent,
    )

from domain_events.rabbitmq_transport import get_transport


class TestEvent(object):

    def test_fire_event(self):
        """Use basic API to fire event"""
        event = emit_domain_event('test.test', {})
        flush()
        json_data, routing_key = get_transport().messages[-1]
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_event_loading(self):
        event = emit_domain_event('test.test', {})
        flush()
        json_data, routing_key = get_transport().messages[-1]

        new_event = DomainEvent.from_json(json_data)
        assert new_event == event

    def test_pending_until_flushed(self):
        emit_domain_event('test.test', {})
        assert get_transport().pending
        flush()
        assert not get_transport().pending
