# Sentinel object indicating the default broker should be used.
# Allows passing `None` to deactivate broker connections in develop and test
# environments.
DEFAULT = object()

# The connection settings used for connecting to RabbitMQ broker.
# Default settings are for a local installation of RabbitMQ.
BROKER = 'amqp://guest:guest@localhost:5672/%2F'
