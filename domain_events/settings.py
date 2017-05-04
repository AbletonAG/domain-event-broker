try:
    from django.conf import settings as django_settings
except ImportError:
    django_settings = None

# Default settings for local installation of RabbitMQ
DEFAULT_BROKER = 'amqp://guest:guest@localhost:5672/%2F'

BROKER = DEFAULT_BROKER

if django_settings is not None:
    BROKER = getattr(django_settings, 'DOMAIN_EVENT_BROKER', BROKER)

# It's possible to connect to different brokers when sending or consuming
# domain events.
PRODUCER_BROKER = BROKER
CONSUMER_BROKER = BROKER

if django_settings and getattr(django_settings, 'DOMAIN_EVENT_PRODUCER_BROKER'):
    PRODUCER_BROKER = django_settings.DOMAIN_EVENT_PRODUCER_BROKER

if django_settings and getattr(django_settings, 'DOMAIN_EVENT_CONSUMER_BROKER'):
    CONSUMER_BROKER = django_settings.DOMAIN_EVENT_CONSUMER_BROKER
