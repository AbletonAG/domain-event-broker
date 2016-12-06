# __init__.py

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from transport import (
    configure,
    discard,
    emit_domain_event,
    transmit,
    DEFAULT_CONNECTION_SETTINGS,
    Receiver,
    Retry,
    Sender,
    SingleQueueReceiver,
)

from events import (
    DomainEvent,
)
