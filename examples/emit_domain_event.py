#!/usr/bin/env python

import sys

from abl.util import Bunch

from domain_events import *

connection_settings=Bunch(
    RABBITMQ_HOST='localhost',
    RABBITMQ_PORT=None,
    RABBITMQ_USER=None,
    RABBITMQ_PW=None,
)

initialize_connection_settings(connection_settings)

def main():
    # default settings are for sending domain events
    queue = create_queue()

    event = DomainEvent('test_domain', 'event_has_happened', data={'myinfo':'foo'})

    fire_domain_event(queue, event)
    print " [x] Sent %r" % event

if __name__ == '__main__':
    main()
