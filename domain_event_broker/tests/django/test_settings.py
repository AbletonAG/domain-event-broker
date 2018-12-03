SECRET_KEY = 'test'
INSTALLED_APPS = [
    "domain_event_broker.django",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'domain_event_broker',
    }
}
