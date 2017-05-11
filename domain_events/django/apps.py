from django.apps import AppConfig
from django.conf import settings as djsettings

from domain_events import settings


class DomainEventsConfig(AppConfig):
    name = 'domain_events.django'
    label = 'domain_events_django'
    verbose_name = 'Domain Events'

    def ready(self):
        if hasattr(djsettings, 'DOMAIN_EVENT_BROKER'):
            settings.BROKER = djsettings.DOMAIN_EVENT_BROKER
