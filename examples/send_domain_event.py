#!/usr/bin/env python
import logging

from domain_events import publish_domain_event

logging.basicConfig()


def main():
    event = publish_domain_event('test_domain.event_has_happened', data={'myinfo':'foo'})
    print " [x] Sent %r" % event


if __name__ == '__main__':
    main()
