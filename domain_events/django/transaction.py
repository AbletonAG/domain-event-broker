from django.db import transaction
from domain_events import send_domain_event


def send_on_commit(*args, **kwargs):
    """
    Send domain event after transaction has been committed to the database. If
    there is no transaction, it'll be sent right away. If atomic blocks are
    nested, it will be sent when exiting the outermost atomic block.

    More information can be found here:

    https://docs.djangoproject.com/en/dev/topics/db/transactions/#performing-actions-after-commit
    """
    def send():
        send_domain_event(*args, **kwargs)

    transaction.on_commit(send)
