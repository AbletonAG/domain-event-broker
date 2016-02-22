from datetime import datetime
import json
from uuid import uuid4

import rabbitmq_transport


FACTOR = 10**6


def get_domain_events_sender(connection_settings):
    pass


def to_timestamp(dt, epoch=datetime(1970,1,1)):
    """http://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python"""
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * FACTOR) / FACTOR


class DomainEvent(object):

    def __init__(self,
                 routing_key=u"",
                 data={},
                 domain_object_id=None,
                 uuid_string=None, # only set if recreated from json repr
                 timestamp=None, # only set if recreated from json repr
                 **kwargs):
        """Define a Domain Event
        @routing_key -> str : The routing key is of the form <DOMAIN>.<EVENT_TYPE>
            The routing key should be a descriptive name of the domain event such as
            "user.has_unlocked_serial_number".
        @data -> dict : the actual event data. MUST be json serializable.
        @domain_object_id -> str : this MIGHT be set if the event is about a domain object with a known domain id.
            NOTE: this field is optional. If used, it might search in an event store easier.
        @uuid_string -> str : this events uuid4. If left None, a new one will be created.
            NOTE: a uuid object can not be serialized in json.
        @timestamp -> float : unix timestamp. If timestamp is None, a new (utc) timestamp will be created.
            NOTE: a datetime object can not be serialized in json.

        ASSUMPTION: when sending and receiving an event,
        we have a one to one correspondence between event type and queue.
        If a receiver receives more than one event type, one need to use the lower queue primitives.

        The routing key is of the form <DOMAIN>.<EVENT_TYPE>
        """
        self.routing_key = routing_key
        self.data = data
        self.domain_object_id = domain_object_id
        self.uuid_string = uuid_string
        if uuid_string is None:
            self.uuid_string = str(uuid4())
        self.timestamp = timestamp
        if timestamp is None:
            timestamp = to_timestamp(datetime.utcnow())
            self.timestamp = timestamp
        event_data = self.__dict__.copy()
        self.event_data = event_data

    @classmethod
    def from_json(cls, json_data):
        """Create a DomainEvent from json_data. Note that you probably want to dispatch first based on
        domain and event type
        """
        return cls(**json.loads(json_data))

    @classmethod
    def create_and_fire(cls, *args, **kwargs):
        event = cls(*args, **kwargs)
        _fire_domain_event(event)

        return event

    def __repr__(self):
        return u"DomainEvent('{}', '{}', (domain_obj_id: {}))".format(
            self.routing_key,
            self.data,
            self.domain_object_id,
        )

    __str__ = __repr__

    def __eq__(self, other):
        return self.event_data == other.event_data


def emit_domain_event(*args, **kwargs):
    return DomainEvent.create_and_fire(*args, **kwargs)


def _fire_domain_event(event, transport=None, request_finished=None):
    """Fire the Domain Event
    @event -> DomainEvent
    @transport: the transport is used to actually fire the event (a RabbitQueue is known to have the
        right API)
    @request_finished: see django.core.signals.request_finished
    """
    if transport is None:
        transport = rabbitmq_transport.default_sender_queue
    assert transport is not None, "We need a transport when firing an event"
    data = json.dumps(event.event_data)
    if request_finished is None:
        transport.send(data, event.routing_key)
    else: # hook into django's request finished signal
        def _flush(sender, **kwargs):
            transport.flush()
            request_finished.disconnect(_flush, dispatch_uid=event.routing_key)
        transport.push(data, event.routing_key)
        request_finished.connect(_flush, dispatch_uid=event.routing_key)
