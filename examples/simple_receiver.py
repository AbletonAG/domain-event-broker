#!/usr/bin/env python

import sys

from domain_events import configure, receive_domain_events, DEFAULT_CONNECTION_SETTINGS

configure(DEFAULT_CONNECTION_SETTINGS)


def log_event(event):
    print " [x] {}".format(event)


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    receive_domain_events(log_event, name='simple-receiver', binding_keys=binding_keys)
