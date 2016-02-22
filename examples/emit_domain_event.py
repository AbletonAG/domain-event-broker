#!/usr/bin/env python
import logging

from domain_events import emit_domain_event, configure

logging.basicConfig()

connection_settings = ''

configure(connection_settings)

def main():
    event = emit_domain_event('test_domain.event_has_happened', data={'myinfo':'foo'})
    print " [x] Sent %r" % event

if __name__ == '__main__':
    main()
