import json
from uuid import uuid1

class DomainEvent(object):

    TRANSPORT = None

    def __init__(self, domain="", event_type="", data={}, domain_object_id=None, uuid_string=None, **kwargs):
        """Define a Domain Event
        @domain -> str : the domain this event is supposed to live
        @event_type -> str : the serialized event type
        @data -> dict : the actual event data
        @domain_object_id -> str : this MIGHT be set if the event is about a domain object with a known domain id
            (if everything lives in a database, this might be the database id)
        @uuid_string -> str : this events uuid1. If left None, a new one will be created. A uuid1 contains
            a timestamp

        NOTES: currently, json does not serialize UUID objects. Since the uuid string is all that matters,
        the easy way out is to just use the string version.
        """
        self.domain = domain
        self.event_type = event_type
        self.routing_key = u"{}.{}".format(domain, event_type)
        self.data = data
        self.domain_object_id=domain_object_id
        self.uuid_string = str(uuid_string)
        if uuid_string is None:
            self.uuid_string = str(uuid1())
        self.request_finished = None
        event_data = self.__dict__.copy()
        del event_data['request_finished']
        self.event_data = event_data

    def __eq__(self, other):
        return self.event_data == other.event_data

    @classmethod
    def from_json(cls, json_data):
        return cls(**json.loads(json_data))

def fire_domain_event(event, transport=None, request_finished=None):
    """Fire the Domain Event
    @event -> DomainEvent
    @transport: the transport is used to actually fire the event (a RabbitQueue is known to have the
        right API)
    @request_finished: see django.core.signals.request_finished
    """
    transport = transport or event.TRANSPORT
    data = json.dumps(event.event_data)
    assert transport is not None, "To fire a Domain Event, a transport must be present"
    if request_finished is None:
        transport.send(data, event.routing_key)
    else: # hook into django's request finished signal
        def _flush(sender, **kwargs):
            transport.flush()
            request_finished.disconnect(_flush, dispatch_uid=event.routing_key)
        transport.push(data, event.routing_key)
        request_finished.connect(_flush, dispatch_uid=event.routing_key)
