# __init__.py

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from rabbitmq_transport import (
    create_queue,
    initialize_connection_settings,
    QueueSettings,
)

from events import DomainEvent, fire_domain_event
