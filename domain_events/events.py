from datetime import datetime
import json
from uuid import uuid4

from .rabbitmq_transport import QueueSettings, DummyQueue, create_queue

FACTOR = 10**6

def get_domain_events_sender(connection_settings):
    pass

def to_timestamp(dt, epoch=datetime(1970,1,1)):
    """http://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python"""
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * FACTOR) / FACTOR

class DomainEvent(object):

    DOMAIN = ""
    EVENT_TYPE = ""
    SEND_TRANSPORT = None
    RECV_TRANSPORT = None
    REQUEST_FINISHED = None # if not None, this needs to be django's request_finished signal

    def __init__(self,
                 domain="",
                 event_type="",
                 data={},
                 domain_object_id=None,
                 uuid_string=None, # only set if recreated from json repr
                 timestamp=None, # only set if recreated from json repr
                 **kwargs):
        """Define a Domain Event
        @domain -> str : the domain this event is supposed to live.
        @event_type -> str : the serialized event type.
        @data -> dict : the actual event data. MUST be json serializable.
        @domain_object_id -> str : this MIGHT be set if the event is about a domain object with a known domain id.
            (if everything lives in a database, this might be the database id)
        @uuid_string -> str : this events uuid4. If left None, a new one will be created.
            NOTE: a uuid object can not be serialized in json.
        @timestamp -> float : unix timestamp. If timestamp is None, a new (utc) timestamp will be created.
            NOTE: a datetime object can not be serialized in json.

        ASSUMPTION: when sending and receiving an event,
        we have a one to one correspondence between event type and queue.
        If a receiver receives more than one event type, one need to use the lower queue primitives.

        The routing key is of the form <DOMAIN>.<EVENT_TYPE>
        """
        self.domain = domain
        self.event_type = event_type
        self.routing_key = u"{}.{}".format(domain, event_type)
        self.data = data
        self.domain_object_id=domain_object_id
        self.uuid_string = str(uuid_string)
        if uuid_string is None:
            self.uuid_string = str(uuid4())
        self.timestamp = timestamp
        if timestamp is None:
            timestamp = to_timestamp(datetime.utcnow())
            self.timestamp = timestamp
        self.request_finished = None
        event_data = self.__dict__.copy()
        del event_data['request_finished']
        self.event_data = event_data

    @classmethod
    def _rabbitmq_receiver_settings(cls):
        name = u"{}.{}".format(cls.DOMAIN, cls.EVENT_TYPE)
        return QueueSettings(name = u"{}.{}".format(cls.DOMAIN, cls.EVENT_TYPE),
                             is_receiver = True,
                             exchange = u"domain-events",
                             exchange_type = u"topic",
                             binding_keys = (name,),
                             durable = True,
                             dlx = False,
                             )
    @classmethod
    def _rabbitmq_sender_settings(cls):
        name = u"{}.{}".format(cls.DOMAIN, cls.EVENT_TYPE)
        settings = cls._rabbitmq_receiver_settings()
        settings.RECEIVER = False

        return settings

    @classmethod
    def rabbitmq_sender_queue(cls, connection_settings, queue_type=DummyQueue):
        queue_settings = cls._rabbitmq_sender_settings()
        queue = queue_type(queue_settings, connection_settings)
        queue.connect()

        return queue

    @classmethod
    def rabbitmq_receiver_queue(cls, connection_settings, queue_type=DummyQueue):
        queue_settings = cls._rabbitmq_receiver_settings()
        queue = queue_type(queue_settings, connection_settings)
        queue.connect()

        return queue


    @classmethod
    def from_json(cls, json_data):
        """Create a DomainEvent from json_data. Note that you probably want to dispatch first based on
        domain and event type
        """
        return cls(**json.loads(json_data))

    @classmethod
    def create(cls, **kwargs):
        """Create a domain event from a subclass, You just need to provide the data.
        """
        return cls(cls.DOMAIN, cls.EVENT_TYPE, **kwargs)

    @classmethod
    def create_and_fire(cls, **kwargs):
        event = cls.create(**kwargs)
        fire_domain_event(None, event)

        return event

    def __repr__(self):
        return u"DomainEvent('{}', '{}', {})".format(self.domain, self.event_type, self.data)

    __str__ = __repr__

    def __eq__(self, other):
        return self.event_data == other.event_data


def fire_domain_event(transport, event, request_finished=None):
    """Fire the Domain Event
    @event -> DomainEvent
    @transport: the transport is used to actually fire the event (a RabbitQueue is known to have the
        right API)
    @request_finished: see django.core.signals.request_finished
    """
    if transport is None:
        transport = event.__class__.SEND_TRANSPORT
    assert transport is not None, "We need a transport when firing an event"
    if request_finished:
        request_finished = event.__class__.REQUEST_FINISHED
    data = json.dumps(event.event_data)
    if request_finished is None:
        transport.send(data, event.routing_key)
    else: # hook into django's request finished signal
        def _flush(sender, **kwargs):
            transport.flush()
            request_finished.disconnect(_flush, dispatch_uid=event.routing_key)
        transport.push(data, event.routing_key)
        request_finished.connect(_flush, dispatch_uid=event.routing_key)
