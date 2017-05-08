from datetime import datetime
import json
from uuid import uuid4

FACTOR = 10**6


def to_timestamp(dt, epoch=datetime(1970, 1, 1)):
    """http://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python"""
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * FACTOR) / FACTOR


class DomainEvent(object):

    def __init__(self,
                 routing_key=u"",
                 data={},
                 domain_object_id=None,
                 uuid_string=None,  # only set if recreated from json repr
                 timestamp=None,  # only set if recreated from json repr
                 retries=0,
                 **kwargs):
        """
        Define a Domain Event.

        :param str routing_key: The routing key is of the form
            ``<DOMAIN>.<EVENT_TYPE>``.  The routing key should be a descriptive
            name of the domain event such as ``user.registered``.
        :param dict data: The actual event data. *Must* be json serializable.
        :param str domain_object_id: Domain identifier of the event. This field
            is optional. If used, it might make search in an event store easier.
        :param str uuid_string: This UUID identifier of the event. If left
            ``None``, a new one will be created.
        :param float timestamp: Unix timestamp. If timestamp is None, a new
            (UTC) timestamp will be created.
        :param int retries: Number of times this event was delivered to a
            subscriber already.
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
        """
        Create a DomainEvent from ``json_data``. Note that you probably want to
        dispatch first based on domain and event type.

        :param str json_data: Serialized domain event data.
        :rtype: DomainEvent
        """
        try:
            json_data = json_data.decode('utf-8')
        except AttributeError:
            pass
        return cls(**json.loads(json_data))

    def __repr__(self):
        return u"DomainEvent('{0.routing_key}', '{0.data}', (domain_obj_id: {0.domain_object_id}, uuid: {0.uuid_string}))".format(self) # noqa

    __str__ = __repr__

    def __eq__(self, other):
        return self.event_data == other.event_data
