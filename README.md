# Domain events

This library provides a shallow layer on top of [RabbitMQ topic
exchanges](https://www.rabbitmq.com/tutorials/tutorial-five-python.html) for
sending and receiving domain events. Sender and receiver need not know about
each other and can be started and stopped in any order. Each receiver controls
their own retry policy, whether they need a durable queue for the time they are
down, or a dead-letter queue in case there is an error in the receiver.

## Configuration

This library needs to connect to RabbitMQ. By default, a local instance of
RabbitMQ is used. This can be changed by calling configure with an [amqp
URL](http://pika.readthedocs.org/en/latest/examples/using_urlparameters.html):

    from domain_events import configure
    configure('amqp://user:password@rabbitmq-host/domain-events')

## Sending events

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

## Receiving events

Receivers can listen to one or more domain events - controlled via the binding
keys. Binding keys may contain wildcards. A queue will be created for each
receiver. RabbitMQ takes care of routing only the relevant events to this
queue.

This script will receive all events that are sent in the user domain:

    from domain_events import Receiver

    def handle_user_event(event):
        print event

    receiver = Receiver()
    receiver.register(handle_user_event, 'printer', ['user.*'])
    receiver.start_consuming()

### Retry policy

If there is a problem consuming a message - for example a web service is down -
the receiver can raise an error to retry handling the event after the given delay:

    from domain_events import Receiver

    def sync_user_data(event):
        try:
            send_to_service(event)
        except ServiceIsDown:
            raise Retry(5.0 ** event.retries) # 1s, 5s, 25s

    receiver = Receiver()
    receiver.register(sync_user_data, 'sync_data', ['user.*'], max_retries=3)
    receiver.start_consuming()

The delayed retries are bound to the consumer, not the event. If `max_retries`
is exceeded, the event will be dropped or dead-lettered.

#### Caveats

The retry policy is implemented using a wait queue with per-message expiry.
Expired messages will only be re-routed to the receiver when the first message
in the waiting queue expires. For the example above, if event A has been
retried for the third time and another event B is retried for the first time,
both events will only be redelivered after event A expires (25s) even though
event A is supposed to expire after 1s.

## Development

Make sure you have RabbitMQ installed locally for testing.

* create virtualenv and activate it
* run `pip install -r requirements.txt -r dev_requirements.txt -e .`
* the only external dependency (so far) is `pika`

## Architecture

There's

* Generic domain events: `domain_events.events`
* The transport, via rabbitmq: `domain_events.transport`

## Testing

Testing is done by `py.test` which allows some quite advanced testing features.
