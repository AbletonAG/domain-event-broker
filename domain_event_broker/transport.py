from concurrent.futures import ThreadPoolExecutor
from functools import partial
import logging
import json
from pika import (
    BasicProperties,
    BlockingConnection,
    URLParameters,
    )
from .events import DomainEvent
from . import settings

log = logging.getLogger(__name__)


def publish_domain_event(routing_key, data, domain_object_id=None,
                         uuid_string=None, timestamp=None,
                         connection_settings=settings.DEFAULT):
    """
    Send a domain event to the message broker. The broker will take care of
    dispatching the event to registered subscribers.

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
    :param str connection_settings: Specify the broker with an AMQP URL. If not
        given, the default broker will be used. If set to ``None``, the domain
        event is not published to a broker.
    :return: The domain event that was published.
    :rtype: :py:class:`domain_event_broker.DomainEvent`
    """
    event = DomainEvent(
        routing_key=routing_key,
        data=data,
        domain_object_id=domain_object_id,
        uuid_string=uuid_string,
        timestamp=timestamp)
    data = json.dumps(event.event_data)
    publisher = Publisher(connection_settings)
    publisher.publish(data, event.routing_key)
    publisher.disconnect()
    return event


class Retry(Exception):
    """
    Raise this exception in an event handler to schedule a delayed retry. The
    delay is specified in seconds.

    .. note::

        Internally a delay exchange with a per-message TTL is used and all
        delayed events for a handler that share the same delay are placed in
        one queue. The RabbitMQ TTL has a Millisecond resolution.
    """
    def __init__(self, delay=10.0):
        super(Retry, self).__init__()
        self.delay = delay


def _retry_message(name, retry_exchange, channel, method, properties, body,
                   delay):
    delay = int(delay * 1000)
    # Create queue that should be automatically deleted shortly after
    # the last message expires. The queue is re-declared for each retry
    # which resets the queue expiry.
    delay_name = '{}-delay-{}'.format(name, delay)
    result = channel.queue_declare(
        queue=delay_name,
        durable=True,
        arguments={
            'x-dead-letter-exchange': retry_exchange,
            'x-message-ttl': delay,
            'x-expires': delay + 10000,
            },
        )
    queue_name = result.method.queue
    # Bind the wait queue to the delay exchange before publishing
    channel.exchange_declare(
        exchange=delay_name,
        durable=True,
        auto_delete=True,  # Delete exchange when queue is deleted
        exchange_type='topic')
    channel.queue_bind(
        exchange=delay_name,
        routing_key='#',
        queue=queue_name)
    channel.basic_publish(
        exchange=delay_name,
        routing_key=method.routing_key,
        body=body,
        properties=properties)


def _call_event_handler(handler, event, connection, acknowledge, retry,
                        reject, max_retries):
    # The handler is executed in a separate worker thread. Handle any errors
    # and trigger retries, dead-lettering or acknowledgement via threadsafe
    # callback on the connection.
    try:
        handler(event)
    except Retry as error:
        if event.retries < max_retries:
            # Publish manually to the delay exchange with a per-message TTL
            msg = "Retry ({retries}) consuming event {event} in {delay:.1f}s"
            log.info(msg.format(
                event=event,
                retries=event.retries,
                delay=error.delay))
            delayed_retry = partial(retry, delay=error.delay)
            connection.add_callback_threadsafe(acknowledge)
            connection.add_callback_threadsafe(delayed_retry)
        else:
            # Reject puts the message into the dead-letter queue if there is
            # one, otherwise the message is discarded.
            msg = "Exceeded max retries ({}) for {} event".format(
                max_retries, event.routing_key)
            log.error(msg, exc_info=True, extra=event.event_data)
            connection.add_callback_threadsafe(reject)
    except:  # noqa: E722
        # Note: If we want immediate requeueing, add a `RequeueError`
        # that a consumer can raise to trigger requeuing. Dead-letter
        # queues are a better choice in most cases.
        connection.add_callback_threadsafe(reject)
        log.exception("Event has been dead-lettered or discarded")
    else:
        connection.add_callback_threadsafe(acknowledge)


def receive_callback(transport, handler, name, retry_exchange, max_retries,
                     channel, method, properties, body):
    try:
        event = DomainEvent.from_json(body)
    except Exception:
        # We cannot parse the message; requeuing would not help.
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        log.exception("Failed to load message: %s", body)
    else:
        if properties.headers and 'x-death' in properties.headers:
            # Older RabbitMQ versions (< 3.5) keep adding x-death entries, new
            # versions only keep the most recent entry and increment 'count',
            # see: https://github.com/rabbitmq/rabbitmq-server/issues/78
            expiry_info = properties.headers['x-death'][0]
            if 'count' in expiry_info:
                event.retries = expiry_info['count']
            else:
                event.retries = len(properties.headers['x-death'])
        log.debug("Received {}:{}".format(method.routing_key, event))

        # The channel and connection objects are not threadsafe. Only call any
        # of those function from the main thread via a threadsafe callback.
        acknowledge = partial(
            channel.basic_ack,
            delivery_tag=method.delivery_tag)
        reject = partial(
            channel.basic_reject,
            delivery_tag=method.delivery_tag,
            requeue=False)
        retry = partial(
            _retry_message,
            name=name,
            retry_exchange=retry_exchange,
            channel=channel,
            method=method,
            properties=properties,
            body=body)
        event_handler = partial(
            _call_event_handler,
            handler=handler,
            event=event,
            connection=channel.connection,
            acknowledge=acknowledge,
            retry=retry,
            reject=reject,
            max_retries=max_retries)
        transport.workers.submit(event_handler)


def requires_broker(method):
    """
    If connection_settings are set to ``None`` on the transport object, don't
    perform the action and log the call instead. This is used for environments
    where no broker is available, e.g. development and testing.
    """
    def wrapper(transport, *args, **kwargs):
        if transport.connection_settings is None:
            log.debug("No broker configured: {}.{}() is deactivated.".format(
                transport.__class__.__name__,
                method.__name__))
        else:
            return method(transport, *args, **kwargs)
    return wrapper


class Transport(object):

    def __init__(self, connection_settings=settings.DEFAULT,
                 exchange="domain-events", exchange_type="topic"):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.context_depth = 0
        self.pending = []
        self.connection = None
        self.messages = []
        if connection_settings is settings.DEFAULT:
            connection_settings = settings.BROKER
        self.connection_settings = connection_settings
        self.channel = None
        self.connect()

    @requires_broker
    def connect(self):
        """
        For now we use a synchronous connection - caller is blocked until a
        message is added to the queue. We might switch to asynch connections
        should this incur noticable latencies.
        """
        params = URLParameters(self.connection_settings)
        self.connection = BlockingConnection(params)
        self.channel = self.connection.channel()

        # set up the Exchange (if it does not exist)
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=True,
            auto_delete=False)

    @requires_broker
    def disconnect(self):
        """
        Disconnect from queue. The API is a little weird. First we close the
        connection, then disconnect from the socket. The last step will remove
        the connection from the RabbitMQ connection pool.

        Make sure you don't close the channel, otherwise the connection cannot
        be closed anymore.
        """
        self.connection.close()
        self.channel = None
        self.connection = None


class Publisher(Transport):

    @requires_broker
    def publish(self, message, routing_key=None):
        """
        Send as persistent message.
        """
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=message,
            properties=BasicProperties(delivery_mode=2),
            )


class Subscriber(Transport):
    """
    A subscriber manages the registration of one or more event handlers. Once
    instantiated, call ``register`` to add subscribers and ``start_consuming``
    to wait for incoming events.

    .. note::

        The subscriber only uses one thread for processing events. Even if
        multiple handlers are registered, only one event is processed at a
        time.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workers = ThreadPoolExecutor(max_workers=1)

    @requires_broker
    def bind_routing_keys(self, exchange, queue_name, binding_keys):
        for binding_key in binding_keys:
            self.channel.queue_bind(
                exchange=exchange,
                routing_key=binding_key,
                queue=queue_name)

    @requires_broker
    def register(self, handler, name, binding_keys=(), dead_letter=False,
                 durable=True, exclusive=False, auto_delete=False,
                 max_retries=0):
        """
        Register a handler for one or more types of domain events.

        :param function handler: This function will be called when an event
            happens. It receives a ``DomainEvent`` as the only parameter.
        :param str name: Name of the handler. Used as the queue name.
        :param tuple|list binding_keys: One or more routing keys, e.g.
            ``["user.registered", "user.imported"]``. The binding keys may
            include wildcards. Use ``user.*`` to subscribe to all events in the
            user domain. Use ``#`` to call ``handler`` for all domain events
            across all domains.
        :param bool dead_letter: Whether to store events in a dead-letter queue
            if the handler raises an exception while processing the event.
        :param int max_retries: The handler may raise ``domain_event_broker.Retry``
            to indicate the event processing should be retried later. This
            parameter controls how often an event is rescheduled before it is
            dead-lettered or discarded.
        """
        retry_exchange = name + '-retry'
        dead_letter_exchange = name + '-dlx'

        arguments = {}
        if dead_letter:
            self.channel.exchange_declare(
                exchange=dead_letter_exchange,
                exchange_type=self.exchange_type)
            result = self.channel.queue_declare(
                queue=name + '-dl',
                durable=True)
            queue_name = result.method.queue
            self.bind_routing_keys(
                dead_letter_exchange,
                queue_name,
                binding_keys)
            arguments["x-dead-letter-exchange"] = dead_letter_exchange

        # Create subscriber queue and bind to the default exchange
        self.channel.queue_declare(
            queue=name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments)
        self.bind_routing_keys(self.exchange, name, binding_keys)

        # Re-route failed messages to a retry dead letter queue.
        # This is only used if max_retries > 0 but we set up the exchanges
        # anyway so that messages can be replayed manually in the consumer
        # context.
        # Declare the exchange where messages expired in the wait queue are
        # routed.
        self.channel.exchange_declare(
            exchange=retry_exchange,
            exchange_type=self.exchange_type)
        # Bind the consumer queue to the retry exchange
        self.bind_routing_keys(retry_exchange, name, binding_keys)

        callback = partial(
            receive_callback,
            self,
            handler,
            name,
            retry_exchange,
            max_retries)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=name, on_message_callback=callback)

    @requires_broker
    def stop_consuming(self):
        self.channel.stop_consuming()
        self.disconnect()

    @requires_broker
    def start_consuming(self, timeout=None):
        """
        Enter IO consumer loop after calling `register`. If timeout is given,
        the consumer will be stopped after the specified number of seconds.
        """
        if timeout:
            self.connection.call_later(timeout, self.stop_consuming)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()
        except:  # noqa: E722
            self.stop_consuming()
            raise
