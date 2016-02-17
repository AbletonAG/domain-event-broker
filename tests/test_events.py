import json

from abl.util import Bunch

import pytest

from tests.test_queues import get_queue
from domain_events import *

initialize_lib(None) # we are using the dummy queue

from domain_events.rabbitmq_transport import default_sender_queue as transport

class TestEvent(object):

    def test_fire_event(self):
        event = DomainEvent('test', 'test', {})
        fire_domain_event(event)
        json_data, routing_key = transport.last_message
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_alternative_fireing(self):
        event = DomainEvent.create_and_fire('test', 'test', {})
        json_data, routing_key = transport.last_message
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string


    def test_event_loading(self):
        event = DomainEvent('test', 'test', {})
        fire_domain_event(event)
        json_data, routing_key = transport.last_message

        new_event = DomainEvent.from_json(json_data)
        assert new_event == event

    def test_event_subclass(self):
        class SubDomainEvent(DomainEvent):
            DOMAIN = 'test'
            EVENT_TYPE = 'test'

        event = SubDomainEvent.create_and_fire(data={})
        json_data, routing_key = transport.last_message
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string
