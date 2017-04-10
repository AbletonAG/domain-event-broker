import json
from mock import patch

from domain_events import DomainEvent, send_domain_event


@patch('domain_events.transport.Sender.send')
class TestEvent(object):

    def test_fire_event(self, mock):
        """Use basic API to fire event"""
        event = send_domain_event('test.test', {})
        assert mock.called
        json_data, routing_key = mock.call_args[0]
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_event_loading(self, mock):
        event = send_domain_event('test.test', {})
        assert mock.called
        json_data, routing_key = mock.call_args[0]
        new_event = DomainEvent.from_json(json_data)
        assert new_event == event
