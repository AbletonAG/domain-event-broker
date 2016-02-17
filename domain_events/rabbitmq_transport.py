import logging
from pika import (
    BasicProperties,
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
    )

log = logging.getLogger(__name__)

_connection_settings = None
default_sender_queue = None


def initialize_lib(connection_settings):
    global _connection_settings
    _connection_settings = connection_settings

    global default_sender_queue
    if default_sender_queue is None:
        default_sender_queue = create_queue()
        default_sender_queue.connect()


class TransactionInProgressError(Exception):
    pass

class QueueSettings(object):

    def __init__(self,
                 name="",
                 is_receiver=False,
                 exchange="domain-events",
                 exchange_type="topic",
                 binding_keys=(),
                 durable=True,
                 dlx=False):
        """The Rabbitmq Queue Settings.
        The defaults will be good to send events to the 'domain-events' topic exchange.
        """
        self.NAME = name
        self.IS_RECEIVER = is_receiver
        self.EXCHANGE = exchange
        self.EXCHANGE_TYPE = exchange_type
        self.BINDING_KEYS = binding_keys
        self.DURABLE = durable
        self.DLX = dlx


class DummyQueue(object):

    def __init__(self,
                 queue_settings=None,
                 connection_settings=None,
                 db_transaction=None,
                 receive_callback=None
                 ):
        self.queue_settings = queue_settings
        if queue_settings is None:
            self.queue_settings = QueueSettings() # we default to sending to the domain-events topic exchange
        self.context_depth = 0
        self.pending = []
        self.connection = None
        self.messages = []
        self.last_message = None
        self.connection_settings = connection_settings or _connection_settings
        self.db_transaction = db_transaction
        self.channel = None
        self.receive_callback = receive_callback
        if receive_callback is None:
            self.receive_callback = self.fallback_receive_callback

    def push(self, data, routing_key=None):
        self.pending.append((data, routing_key))
        log.debug("Pushed a message into queue {}: {}".format(
                self.queue_settings.NAME, (data, routing_key)))

    def flush(self):
        """
        Open connection prior to transmitting the payload and close right
        after. We could keep the connection open for subsequent requests but
        events won't occur that often to justify the additional housekeeping.
        The whole roundtrip takes about 5-10ms.

        This needs to happen after the DB transaction is committed. All
        messages pushed since the last flush are now transmitted to the queuing
        service.
        """
        if self.db_transaction is not None:
            current_connection = self.db_transaction.get_connection()
            if current_connection.in_atomic_block:
                log.warning("Called flush in atomic block")
        log.debug("Flushing {} queue, sending {} messages.".format(
                self.queue_settings.NAME, len(self.pending)))

        if self.pending:
            with self:
                for message, routing_key in self.pending:
                    self.send(message, routing_key)
        self.pending = []

    def connect(self):
        pass

    def disconnect(self):
        pass

    def send(self, message, routing_key=None):
        self.messages.append((message, routing_key))
        self.last_message = self.messages[-1]

    def fallback_receive_callback(self, ch, method, properties, body):
        """
        Please make sure to initialize the receive_callback if you need one.
        """
        print " [x] %r:%r" % (method.routing_key, body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def receive(self):
        self.channel.basic_consume(self.receive_callback, queue=self.queue_settings.NAME)
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


class RabbitQueue(DummyQueue):

    def __init__(self, **kwargs):
        super(RabbitQueue, self).__init__(**kwargs)
        if self.connection_settings is None:
            raise ValueError("RabbitQueue needs settings")

    def connect(self):
        """
        For now we use a synchronous connection - caller is blocked until a
        message is added to the queue. We might switch to asynch connections
        should this incur noticable latencies.
        """
        credentials = None
        if self.connection_settings.RABBITMQ_USER and self.connection_settings.RABBITMQ_PW:
            credentials = PlainCredentials(
                self.connection_settings.RABBITMQ_USER,
                self.connection_settings.RABBITMQ_PW,
                )
        params = ConnectionParameters(
            host=self.connection_settings.RABBITMQ_HOST,
            port=self.connection_settings.RABBITMQ_PORT,
            credentials=credentials,
            )
        self.connection = BlockingConnection(params)
        self.channel = self.connection.channel()

        if self.queue_settings.EXCHANGE and self.queue_settings.EXCHANGE_TYPE:
            # set up the Exchange (if it does not exist)
            self.channel.exchange_declare(exchange=self.queue_settings.EXCHANGE,
                                          type=self.queue_settings.EXCHANGE_TYPE,
                                          durable=True,
                                          auto_delete=False,
                                          )
        if self.queue_settings.IS_RECEIVER:
            arguments = {"x-dead-letter-exchange": self.queue_settings.DLX} if self.queue_settings.DLX else {}
            self.channel.queue_declare(queue=self.queue_settings.NAME,
                                       durable=self.queue_settings.DURABLE,
                                       arguments=arguments,
                                       )
            if self.queue_settings.BINDING_KEYS is not None:
                for binding_key in self.queue_settings.BINDING_KEYS:
                    self.channel.queue_bind(queue=self.queue_settings.NAME,
                                            exchange=self.queue_settings.EXCHANGE,
                                            routing_key=binding_key)

    def send(self, message, routing_key=None):
        """
        Send as persistent message.
        """
        if routing_key is None:
            routing_key = self.queue_settings.NAME
        super(RabbitQueue, self).send(message)
        with self:
            self.channel.basic_publish(
                exchange=self.queue_settings.EXCHANGE,
                routing_key=routing_key,
                body=message,
                properties=BasicProperties(delivery_mode=2),
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


def create_queue(**kwargs):
    connection_settings = kwargs.get('connection_settings') or _connection_settings
    if connection_settings and connection_settings.RABBITMQ_HOST:
        return RabbitQueue(**kwargs)
    else:
        return DummyQueue(**kwargs)
