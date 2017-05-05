#!/usr/bin/env python

import logging
import sys

from domain_events import Subscriber, Retry


logging.basicConfig(level=logging.INFO)


def handler(event):
    delay = 5.0 + (10.0 * event.retries)
    raise Retry(delay)


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    subscriber = Subscriber()
    subscriber.register(handler, name='retry-ronny', binding_keys=binding_keys, max_retries=3)
    subscriber.start_consuming()
