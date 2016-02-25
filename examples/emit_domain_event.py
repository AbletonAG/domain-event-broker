#!/usr/bin/env python
import logging

from domain_events import emit_domain_event, flush

logging.basicConfig()


def main():
    event = emit_domain_event('test_domain.event_has_happened', data={'myinfo':'foo'})
    flush()
    print " [x] Sent %r" % event


if __name__ == '__main__':
    main()
