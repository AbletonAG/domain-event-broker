#!/usr/bin/env python

import sys

from domain_events import Subscriber


def handler(event):
    raise Exception("I can't handle that.")


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    subscriber = Subscriber()
    subscriber.register(handler, name='stumbling-steve', binding_keys=binding_keys, dead_letter=True)
    subscriber.start_consuming()
