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


def send_domain_event(*args, **kwargs):
    connection_settings = kwargs.pop('connection_settings', settings.PRODUCER_BROKER)
    event = DomainEvent(*args, **kwargs)
    data = json.dumps(event.event_data)
    sender = Sender(connection_settings)
    sender.send(data, event.routing_key)
    sender.disconnect()
    return event


class Retry(Exception):
    def __init__(self, delay=10.0):
        super(Retry, self).__init__()
        self.delay = delay


def receive_callback(handler, delay_exchange, max_retries, channel, method, properties, body):
    event = DomainEvent.from_json(body)
    if properties.headers and 'x-death' in properties.headers:
        # Older RabbitMQ versions (< 3.5) keep adding x-death entries, new
        # versions only keep the most recent entry and increment 'count', see:
        # https://github.com/rabbitmq/rabbitmq-server/issues/78
        expiry_info = properties.headers['x-death'][0]
        if 'count' in expiry_info:
            event.retries = expiry_info['count']
        else:
            event.retries = len(properties.headers['x-death'])
    log.debug("Received {}:{}".format(method.routing_key, event))
    try:
        handler(event)
    except Retry as error:
        if event.retries < max_retries:
            # Publish manually to the delay exchange with a per-message TTL
            log.info("Retry ({event.retries}) consuming event {event} in {delay:.1f}s".format(event=event, delay=error.delay))
            channel.basic_ack(delivery_tag=method.delivery_tag)
            properties.expiration = str(int(error.delay * 1000))
            channel.basic_publish(exchange=delay_exchange,
                                  routing_key=method.routing_key,
                                  body=body,
                                  properties=properties,
                                  )
        else:
            # Reject puts the message into the dead-letter queue if there is one
            log.warning("Exceeded max retries ({}) for event {}".format(max_retries, event))
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    except:
        # Note: If we want immediate requeueing, add a `RequeueError` that
        # a consumer can raise to trigger requeuing. Dead-letter queues are
        # a better choice in most cases.
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        raise
    else:
        channel.basic_ack(delivery_tag=method.delivery_tag)


class Transport(object):

    DEFAULT_BROKER = settings.BROKER

    def __init__(self, connection_settings=None,
                 exchange="domain-events", exchange_type="topic"):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.context_depth = 0
        self.pending = []
        self.connection = None
        self.messages = []
        if connection_settings is None:
            connection_settings = self.DEFAULT_BROKER
        self.connection_settings = connection_settings
        self.channel = None
        self.connect()

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
        self.channel.exchange_declare(exchange=self.exchange,
                                      type=self.exchange_type,
                                      durable=True,
                                      auto_delete=False,
                                      )

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


class Sender(Transport):

    DEFAULT_BROKER = settings.PRODUCER_BROKER

    def send(self, message, routing_key=None):
        """
        Send as persistent message.
        """
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=message,
            properties=BasicProperties(delivery_mode=2),
            )


class Receiver(Transport):

    DEFAULT_BROKER = settings.CONSUMER_BROKER

    def bind_routing_keys(self, exchange, queue_name, binding_keys):
        for binding_key in binding_keys:
            self.channel.queue_bind(exchange=exchange,
                                    routing_key=binding_key,
                                    queue=queue_name)

    def register(self, handler, name, binding_keys=(), dead_letter=False,
                 durable=True, exclusive=False, auto_delete=False,
                 max_retries=0):
        retry_exchange = name + '-retry'
        delay_exchange = name + '-delay'
        dead_letter_exchange = name + '-dlx'

        arguments = {}
        if dead_letter:
            self.channel.exchange_declare(exchange=dead_letter_exchange, type=self.exchange_type)
            result = self.channel.queue_declare(queue=name + '-dl', durable=True)
            queue_name = result.method.queue
            self.bind_routing_keys(dead_letter_exchange, queue_name, binding_keys)
            arguments["x-dead-letter-exchange"] = dead_letter_exchange

        # Create receiver queue and bind to the default exchange
        self.channel.queue_declare(queue=name,
                                   durable=durable,
                                   exclusive=exclusive,
                                   auto_delete=auto_delete,
                                   arguments=arguments,
                                   )
        self.bind_routing_keys(self.exchange, name, binding_keys)

        # Re-route failed messages to a retry dead letter queue.
        # This is only used if max_retries > 0 but we set up the exchanges
        # anyway so that messages can be replayed manually in the consumer
        # context.
        # Declare the exchange where messages expired in the wait queue are routed
        self.channel.exchange_declare(exchange=retry_exchange, type=self.exchange_type)
        self.channel.exchange_declare(exchange=delay_exchange, type=self.exchange_type)
        retry_arguments = {'x-dead-letter-exchange': retry_exchange}
        result = self.channel.queue_declare(queue=name + '-wait',
                                            durable=durable,
                                            arguments=retry_arguments)
        queue_name = result.method.queue
        self.bind_routing_keys(delay_exchange, queue_name, binding_keys)
        # Bind the consumer queue to the retry exchange
        self.bind_routing_keys(retry_exchange, name, binding_keys)

        callback = partial(receive_callback, handler, delay_exchange, max_retries)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(callback, queue=name)

    def stop_consuming(self):
        self.channel.stop_consuming()
        self.disconnect()

    def start_consuming(self, timeout=None):
        """
        Enter IO consumer loop after calling `register`. If timeout is given,
        the consumer will be stopped after the specified number of seconds.
        """
        if timeout:
            self.connection.add_timeout(timeout, self.stop_consuming)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()
        except:
            self.stop_consuming()
            raise
