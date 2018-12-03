#!/usr/bin/env python

import sys

from domain_event_broker import Subscriber


def log_event(event):
    print(" [x] {}".format(event))


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    subscriber = Subscriber()
    subscriber.register(log_event, name='simple-subscriber', binding_keys=binding_keys)
    subscriber.start_consuming()
