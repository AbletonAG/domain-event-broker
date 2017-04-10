#!/usr/bin/env python
import logging

from domain_events import send_domain_event

logging.basicConfig()


def main():
    event = send_domain_event('test_domain.event_has_happened', data={'myinfo':'foo'})
    print " [x] Sent %r" % event


if __name__ == '__main__':
    main()
