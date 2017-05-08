Introduction
============

Domain events are a concept used in domain-driven design (DDD). Those events
are published from within a bounded context when something happened inside the
domain that is relevant for other domains as well. Domain events are very
useful for sharing information between separate services without establishing
dedicated communication channels.

Domain events are always asynchronous - allowing to completely decouple event
publisher and subscriber.

This library provides a shallow layer on top of `RabbitMQ topic
exchanges <https://www.rabbitmq.com/tutorials/tutorial-five-python.html>`_ for
publishing and receiving domain events. Publisher and subscriber need not know about
each other and can be started and stopped in any order. Each subscriber controls
their own retry policy, whether they need a durable queue for the time they are
down, or a dead-letter queue in case there is an error in the subscriber.

Publish domain events
---------------------

Events can be sent by calling :py:func:`~domain_events.publish_domain_event`::

    from domain_events import publish_domain_event
    publish_domain_event('user.registered', {'user_id': user.id})

Domain events are sent immediately. When emitting domain events from within a
database transaction, it's recommended to defer publishing until the transaction
is committed. Using a commit hook avoids spurious domain events if a
transaction is rolled back after an error.

Subscribe to domain events
--------------------------

Subscribers can listen to one or more domain events - controlled via the binding
keys. Binding keys may contain wildcards. A queue will be created for each
subscriber. RabbitMQ takes care of routing only the relevant events to this
queue.

This script will receive all events that are sent in the user domain::

    from domain_events import Subscriber

    def handle_user_event(event):
        print event

    subscriber = Subscriber()
    subscriber.register(handle_user_event, 'print-user-event', ['user.*'])
    subscriber.start_consuming()
