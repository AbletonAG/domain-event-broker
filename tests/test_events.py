import json

from abl.util import Bunch

import pytest

from tests.test_queues import get_queue
from domain_events.events import DomainEvent, fire_domain_event

class TestEvent(object):

    def setup(self):
        self.transport = get_queue(False)

    def test_fire_event(self):
        event = DomainEvent('test', 'test', {})
        fire_domain_event(self.transport, event)
        json_data, routing_key = self.transport.last_message
        event_data = json.loads(json_data)
        assert routing_key == "test.test"
        assert event_data['data'] == {}
        assert event_data['uuid_string'] == event.uuid_string

    def test_event_loading(self):
        event = DomainEvent('test', 'test', {})
        fire_domain_event(self.transport, event)
        json_data, routing_key = self.transport.last_message

        new_event = DomainEvent.from_json(json_data)
        assert new_event == event

class TestSpecificEvent(object):
    def setup(self):
        # define a sample Event Class
        class MyEvent(DomainEvent):
            DOMAIN = u"MyDomain"
            EVENT_TYPE = u"MyEventType"

            @classmethod
            def my_action_has_happened(cls, action_id):
                data = {'action_id': action_id}
                event = cls.create_and_fire(data=data)

                return event

        self.event_class = MyEvent
        self.connection_settings = Bunch(
            RABBITMQ_HOST='localhost',
            RABBITMQ_PORT=None,
            RABBITMQ_USER=None,
            RABBITMQ_PW=None,
        )

    def test_receiver_settings(self):
        settings = self.event_class._rabbitmq_receiver_settings()
        assert settings.NAME == u"MyDomain.MyEventType"
        assert settings.EXCHANGE == u"domain-events"
        assert settings.BINDING_KEYS == (u"MyDomain.MyEventType",)

    def test_sender_queue(self):
        transport = self.event_class.rabbitmq_sender_queue(self.connection_settings)
        event = self.event_class.create(data={})
        fire_domain_event(transport, event)
        json_data, routing_key = transport.last_message

        new_event = self.event_class.from_json(json_data)
        assert new_event == event

    def test_higher_api(self):
        # initialize the transport and assign it to class
        transport = self.event_class.rabbitmq_sender_queue(self.connection_settings)
        self.event_class.SEND_TRANSPORT = transport

        # fire
        event = self.event_class.my_action_has_happened(1)
        assert event is not None

        # check that event ended up in the queue
        json_data, routing_key = transport.last_message
        new_event = self.event_class.from_json(json_data)
        assert new_event == event
