#!/usr/bin/env python
import logging

from domain_events import emit_domain_event, configure, DEFAULT_CONNECTION_SETTINGS

logging.basicConfig()

configure(DEFAULT_CONNECTION_SETTINGS)


def main():
    event = emit_domain_event('test_domain.event_has_happened', data={'myinfo':'foo'})
    print " [x] Sent %r" % event


if __name__ == '__main__':
    main()
