from argparse import ArgumentParser
import logging
from importlib import import_module
from itertools import chain
from typing import Any, Callable, Iterable, TypeVar

from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import translation

from domain_event_broker import settings, Subscriber


logger = logging.getLogger(__name__)


HandlerReturn = TypeVar('HandlerReturn')


class ResilientSubscriber(Subscriber):
    """
    Ensure that the event handler can connect to the database even if the
    database connection was interrupted since the last event handler executed
    in the worker thread pool. Django only does that automatically for regular
    requests.
    """

    def register(self, handler: Callable[..., HandlerReturn], *args: Any, **kwargs: Any) -> None:

        def wrapper(*args: Any, **kwargs: Any) -> HandlerReturn:
            """
            Close dead database connections before calling the handler in the
            context of the worker thread.
            """
            close_old_connections()
            return handler(*args, **kwargs)

        super().register(wrapper, *args, **kwargs)


class Command(BaseCommand):

    def add_arguments(self, parser: ArgumentParser) -> None:
        channel_choices = settings.DOMAIN_EVENT_RECEIVERS.keys()
        parser.add_argument(
            "--channel",
            default="default",
            choices=channel_choices,
            help="Channel to process.", # noqa
        )
        parser.add_argument(
            "--all-channels",
            action="store_true",
            default=False,
            help="When set, process all channels. By default, only one channel is processed.", # noqa
        )

    def handle(self, *args: Any, **options: Any) -> None:
        translation.activate('en')
        subscriber = ResilientSubscriber()

        module_names: Iterable[str]
        if options["all_channels"]:
            module_names = chain.from_iterable(settings.DOMAIN_EVENT_RECEIVERS.values())
        else:
            module_names = settings.DOMAIN_EVENT_RECEIVERS[options["channel"]]
        for name in module_names:
            logger.info("* Registering receivers from {}".format(name))
            module = import_module(name)
            module.register(subscriber)
        logger.info("Waiting for events. To exit press CTRL+C")
        subscriber.start_consuming()
