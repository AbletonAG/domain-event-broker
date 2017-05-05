SECRET_KEY = 'test'
INSTALLED_APPS = [
    "domain_events.django",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'domain_events',
    }
}
