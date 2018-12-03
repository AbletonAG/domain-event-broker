#!/usr/bin/env python
import logging

from domain_event_broker import publish_domain_event

logging.basicConfig()


def main():
    event = publish_domain_event('test_domain.event_has_happened', data={'myinfo': 'foo'})
    print(" [x] Sent {}".format(event))


if __name__ == '__main__':
    main()
