# __init__.py

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from rabbitmq_transport import (
    create_queue,
    configure,
    QueueSettings,
    DEFAULT_CONNECTION_SETTINGS,
)

from events import (
    DomainEvent,
    emit_domain_event,
)
