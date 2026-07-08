from django.apps import AppConfig
from django.conf import settings as djsettings

from domain_event_broker import settings


class DomainEventsConfig(AppConfig):
    name = 'domain_event_broker'
    label = 'domain_event_broker'
    verbose_name = 'Domain Events'

    def ready(self) -> None:
        if hasattr(djsettings, 'DOMAIN_EVENT_BROKER'):
            settings.BROKER = djsettings.DOMAIN_EVENT_BROKER
        if hasattr(djsettings, 'DOMAIN_EVENT_RECEIVERS'):
            settings.DOMAIN_EVENT_RECEIVERS = djsettings.DOMAIN_EVENT_RECEIVERS
