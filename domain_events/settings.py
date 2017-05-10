# Sentinel object indicating the default broker should be used.
# Allows passing `None` to deactivate broker connections in develop and test
# environments.
DEFAULT = object()

# Default settings for local installation of RabbitMQ
DEFAULT_BROKER = 'amqp://guest:guest@localhost:5672/%2F'

# It's possible to connect to different brokers when publishing or consuming
# domain events.
BROKER = DEFAULT_BROKER
PUBLISHER_BROKER = BROKER
SUBSCRIBER_BROKER = BROKER


def configure(default_broker, publisher_broker=None, subscriber_broker=None):
    global BROKER, PUBLISHER_BROKER, SUBSCRIBER_BROKER
    BROKER = default_broker if default_broker else BROKER
    PUBLISHER_BROKER = publisher_broker if publisher_broker else BROKER
    SUBSCRIBER_BROKER = subscriber_broker if subscriber_broker else BROKER
