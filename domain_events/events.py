from uuid import uuid1

class DomainEvent(object):

    TRANSPORT = None

    def __init__(self, domain, event_type, data, domain_object_id=None, uuid1=None):
        self.domain = domain,
        self.event_type = event_type
        self.data = data
        self.domain_object_id=domain_object_id
        self.uuid1 = uuid1
        if uuid1 is None:
            self.uuid1 = uuid1()

    def fire(self, transport=None):
        transport = transport or self.TRANSPORT
        transport.send(self.data, u"{}.{}".format(self.domain, self.event_type))
