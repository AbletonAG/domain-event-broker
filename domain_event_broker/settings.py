# The connection settings used for connecting to RabbitMQ broker.
# Default settings are for a local installation of RabbitMQ.
BROKER: str = 'amqp://guest:guest@localhost:5672/%2F'

DOMAIN_EVENT_RECEIVERS: dict[str, list[str]] = {
    "default": [],
}
