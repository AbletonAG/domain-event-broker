# Domain event broker

This library provides a shallow layer on top of [RabbitMQ topic
exchanges](https://www.rabbitmq.com/tutorials/tutorial-five-python.html) for
publishing and receiving domain events. Publisher and subscriber need not know about
each other and can be started and stopped in any order. Each subscriber controls
their own retry policy, whether they need a durable queue for the time they are
down, or a dead-letter queue in case there is an error in the subscriber.

## Configuration

This library needs to connect to RabbitMQ. By default, a local instance of
RabbitMQ is used. This can be changed by passing an [amqp
URL](http://pika.readthedocs.org/en/latest/examples/using_urlparameters.html)
to `publish_domain_event` or when instantiating `Publisher` or `Subscriber`:

    from domain_event_broker import Subscriber
    subscriber = Subscriber('amqp://user:password@rabbitmq-host/domain-events')

## Integrations

### Django

This library can be configured via your Django settings. Add
*domain_event_broker.django* to your `INSTALLED_APPS` and set the
`DOMAIN_EVENT_BROKER` in your settings:

    INSTALLED_APPS = (
        'domain_event_broker.django',
        )

    DOMAIN_EVENT_BROKER = 'amqp://user:password@rabbitmq-host/domain-events'

## Sending events

Events can be sent by calling `publish_domain_event`:

    from domain_event_broker import publish_domain_event
    publish_domain_event('user.registered', {'user_id': user.id})

Domain events are sent immediately. When emitting domain events from within a
database transaction, it's recommended to defer publishing until the transaction
is committed. Using a commit hook avoids spurious domain events if a
transaction is rolled back after an error.

## Receiving events

Subscribers can listen to one or more domain events - controlled via the binding
keys. Binding keys may contain wildcards. A queue will be created for each
subscriber. RabbitMQ takes care of routing only the relevant events to this
queue.

This script will receive all events that are sent in the user domain:

    from domain_event_broker import Subscriber

    def handle_user_event(event):
        print event

    subscriber = Subscriber()
    subscriber.register(handle_user_event, 'printer', ['user.*'])
    subscriber.start_consuming()

### Retry policy

If there is a problem consuming a message - for example a web service is down -
the subscriber can raise an error to retry handling the event after the given delay:

    from domain_event_broker import Subscriber

    def sync_user_data(event):
        try:
            publish_to_service(event)
        except ServiceIsDown:
            raise Retry(5.0 ** event.retries) # 1s, 5s, 25s

    subscriber = Subscriber()
    subscriber.register(sync_user_data, 'sync_data', ['user.*'], max_retries=3)
    subscriber.start_consuming()

The delayed retries are bound to the consumer, not the event. If `max_retries`
is exceeded, the event will be dropped or dead-lettered.

## Development

Make sure you have RabbitMQ installed locally for testing.

* create virtualenv and activate it
* run `pip install -r requirements.txt -r dev_requirements.txt -e .`
* the only external dependency (so far) is `pika`

### Architecture

There's

* Generic domain events: `domain_event_broker.events`
* The transport, via rabbitmq: `domain_event_broker.transport`

### Testing

Testing is done with `py.test`.
