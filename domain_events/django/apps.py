from django.apps import AppConfig
from django.conf import settings as djsettings

from domain_events import settings


class DomainEventsConfig(AppConfig):
    name = 'domain_events.django'
    label = 'domain_events_django'
    verbose_name = 'Domain Events'

    def ready(self):
        settings.configure(
            getattr(djsettings, 'DOMAIN_EVENT_BROKER', None),
            getattr(djsettings, 'DOMAIN_EVENT_PRODUCER_BROKER', None),
            getattr(djsettings, 'DOMAIN_EVENT_CONSUMER_BROKER', None),
            )
