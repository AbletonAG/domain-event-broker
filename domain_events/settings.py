# Default settings for local installation of RabbitMQ
DEFAULT_BROKER = 'amqp://guest:guest@localhost:5672/%2F'

# It's possible to connect to different brokers when sending or consuming
# domain events.
BROKER = DEFAULT_BROKER
PRODUCER_BROKER = BROKER
CONSUMER_BROKER = BROKER


def configure(default_broker, producer_broker=None, consumer_broker=None):
    global BROKER, PRODUCER_BROKER, CONSUMER_BROKER
    BROKER = default_broker if default_broker else BROKER
    PRODUCER_BROKER = producer_broker if producer_broker else BROKER
    CONSUMER_BROKER = consumer_broker if consumer_broker else BROKER
