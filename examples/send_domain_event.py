#!/usr/bin/env python
import logging

from domain_events import send_domain_event, DEFAULT_CONNECTION_SETTINGS

logging.basicConfig()


def main():
    event = send_domain_event(DEFAULT_CONNECTION_SETTINGS, 'test_domain.event_has_happened', data={'myinfo':'foo'})
    print " [x] Sent %r" % event


if __name__ == '__main__':
    main()
