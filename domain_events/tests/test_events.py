import json

from domain_events import (
    emit_domain_event,
    discard,
    transmit,
    DomainEvent,
    )

from domain_events.transport import get_transport


class TestEvent(object):

    def test_fire_event(self):
        """Use basic API to fire event"""
        event = emit_domain_event('test.test', {})
        transmit()
        json_data, routing_key = get_transport().messages[-1]
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_event_loading(self):
        event = emit_domain_event('test.test', {})
        transmit()
        json_data, routing_key = get_transport().messages[-1]

        new_event = DomainEvent.from_json(json_data)
        assert new_event == event

    def test_pending_until_transmitted(self):
        emit_domain_event('test.test', {})
        assert get_transport().pending
        transmit()
        assert not get_transport().pending
        assert get_transport().messages

    def test_pending_until_discarded(self):
        emit_domain_event('test.test', {})
        assert get_transport().pending
        discard()
        assert not get_transport().pending
        assert not get_transport().messages
