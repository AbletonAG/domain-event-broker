from django.apps import AppConfig
from django.conf import settings as djsettings

from domain_event_broker import settings


class DomainEventsConfig(AppConfig):
    name = 'domain_event_broker.django'
    label = 'domain_event_broker_django'
    verbose_name = 'Domain Events'

    def ready(self):
        if hasattr(djsettings, 'DOMAIN_EVENT_BROKER'):
            settings.BROKER = djsettings.DOMAIN_EVENT_BROKER
