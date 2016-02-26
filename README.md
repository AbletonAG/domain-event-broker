Domain events
=============

This library provides a shallow layer on top of [RabbitMQ topic
exchanges](https://www.rabbitmq.com/tutorials/tutorial-five-python.html) for
sending and receiving domain events. Sender and receiver need not know about
each other and can be started and stopped in any order. Each receiver controls
their own retry policy, whether they need a durable queue for the time they are
down, or a dead-letter queue in case there is an error in the receiver.

Configuration
-------------

This library needs to connect to RabbitMQ. By default, a local instance of
RabbitMQ is used. This can be changed by calling configure with an [amqp
URL](http://pika.readthedocs.org/en/latest/examples/using_urlparameters.html):

    from domain_events import configure
    configure('amqp://user:password@rabbitmq-host/domain-events')

Sending events
--------------

Events can be sent by calling `emit_domain_event`:

    from domain_events import emit_domain_event
    emit_domain_event('user.disabled', {'user_id': user.id})
    transmit()

Domain events are not sent immediately. Sending is deferred until `transmit` is
called. This makes it easier to deal with services that access the same
database so that domains aren't received before a transaction is committed. To
clear emitted events without sending, `discard` can be used. When using
database transactions, these functions should be called in a middleware or in a
post-transaction hook.

Receiving events
----------------

Receivers can listen to one or more domain events - controlled via the binding
keys. Binding keys may contain wildcards. A queue will be created for each
receiver. RabbitMQ takes care of routing only the relevant events to this
queue.

This script will receive all events that are sent in the user domain:

    from domain_events import receive_domain_events

    def handle_user_event(event):
        print event

    receive_domain_events(handle_user_event, 'printer', ['user.*'])

Development
-----------

Make sure you have RabbitMQ installed locally for testing.

* create virtualenv and activate it
* run `pip install -r requirements.txt -r dev_requirements.txt -e .`
* the only external dependency (so far) is `pika>=0.9.13`

Architecture
------------

There's

* The transport, currently done via rabbitmq: `domain_events.transport`. This should be usable independent of the events.
* Generic domain events: `domain_events.events`

Testing
-------

Testing is currently done by `py.test` which allows some quite advanced testing features.
