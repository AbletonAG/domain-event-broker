import logging
from pika import (
    BasicProperties,
    BlockingConnection,
    URLParameters,
    )

log = logging.getLogger(__name__)

# Default settings for local installation of RabbitMQ
DEFAULT_CONNECTION_SETTINGS = 'amqp://guest:guest@localhost:5672/%2F'

_connection_settings = DEFAULT_CONNECTION_SETTINGS
_transport = None


def configure(connection_settings):
    """
    Override the connection settings for the default transport that is used
    when emitting domain events.
    """
    global _connection_settings
    _connection_settings = connection_settings


def get_transport():
    global _transport
    if _transport is None:
        _transport = Transport()
    return _transport


def transmit():
    if _transport is not None:
        _transport.transmit()


def discard():
    if _transport is not None:
        _transport.discard()


class Transport(object):

    def __init__(self, exchange="domain-events", exchange_type="topic"):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.context_depth = 0
        self.pending = []
        self.connection = None
        self.messages = []
        self.connection_settings = _connection_settings
        self.channel = None

    def push(self, data, routing_key=None):
        self.pending.append((data, routing_key))
        log.debug("Pushed a message into exchange {}: {}".format(
            self.exchange, (data, routing_key)))

    def transmit(self):
        """
        Open connection prior to transmitting the payload and close right
        after. We could keep the connection open for subsequent requests but
        events won't occur that often to justify the additional housekeeping.
        The whole roundtrip takes about 5-10ms.

        This needs to happen after the DB transaction is committed. All
        messages pushed since the last transmit are now transmitted to the queuing
        service.
        """
        log.debug("Flushing exchange {}, sending {} messages.".format(
            self.exchange, len(self.pending)))
        self.messages = []
        if self.pending:
            with self:
                for message, routing_key in self.pending:
                    self.send(message, routing_key)
        self.pending = []

    def discard(self):
        """
        Discard all pending events. This can be called after an error so that
        subsequent requests don't transmit events for actions that have been
        rolled back.
        """
        self.messages = []
        log.debug("Discarding {} messages.".format(len(self.pending)))
        self.pending = []

    def send(self, message, routing_key=None):
        """
        Send as persistent message.
        """
        self.messages.append((message, routing_key))
        with self:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message,
                properties=BasicProperties(delivery_mode=2),
                )

    def receive(self, callback, name, binding_keys=(), durable=True, dlx=False):
        arguments = {"x-dead-letter-exchange": dlx} if dlx else {}
        self.channel.queue_declare(queue=name,
                                   durable=durable,
                                   arguments=arguments,
                                   )
        for binding_key in binding_keys:
            self.channel.queue_bind(queue=name,
                                    exchange=self.exchange,
                                    routing_key=binding_key)
        self.channel.basic_consume(callback, queue=name)
        # TODO-lha: if we need multiple receivers in one process, we should split
        # basic_consume and start_consuming into different methods.
        self.channel.start_consuming()

    def __enter__(self):
        if self.context_depth == 0:
            self.connect()
        self.context_depth += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.context_depth -= 1
        if self.context_depth == 0:
            self.disconnect()
        return False

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
        self.connection = None
