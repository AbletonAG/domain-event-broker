from datetime import datetime
import json
from uuid import uuid4

FACTOR = 10**6


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
                 retries=0,
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

        @retries -> int : Number of times this event was delivered to a consumer already.

        ASSUMPTION: when publishing and receiving an event,
        we have a one to one correspondence between event type and queue.
        If a subscriber receives more than one event type, one need to use the lower queue primitives.

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
        self.retries = retries

    @classmethod
    def from_json(cls, json_data):
        """Create a DomainEvent from json_data. Note that you probably want to dispatch first based on
        domain and event type
        """
        try:
            json_data = json_data.decode('utf-8')
        except AttributeError:
            pass
        return cls(**json.loads(json_data))

    def __repr__(self):
        return u"DomainEvent('{0.routing_key}', '{0.data}', (domain_obj_id: {0.domain_object_id}, uuid: {0.uuid_string}))".format(self)

    __str__ = __repr__

    def __eq__(self, other):
        return self.event_data == other.event_data
