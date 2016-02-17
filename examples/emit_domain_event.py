#!/usr/bin/env python

import logging
import sys

from abl.util import Bunch

from domain_events import *

logging.basicConfig()

connection_settings=Bunch(
    RABBITMQ_HOST='localhost',
    RABBITMQ_PORT=None,
    RABBITMQ_USER=None,
    RABBITMQ_PW=None,
)

initialize_lib(connection_settings)

def main():
    event = DomainEvent.create_and_fire('test_domain', 'event_has_happened', data={'myinfo':'foo'})
    print " [x] Sent %r" % event

if __name__ == '__main__':
    main()
