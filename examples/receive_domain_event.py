#!/usr/bin/env python

import sys

from domain_events import *

configure(DEFAULT_CONNECTION_SETTINGS)


def main():
    name, binding_key = sys.argv[1:]

    queue_settings = QueueSettings(
        name=name,
        is_receiver=True,
        binding_keys=(binding_key,),
    )

    def receive_callback(ch, method, properties, body):
        event = DomainEvent.from_json(body)
        print " [x] %r:%r" % (method.routing_key, event)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    queue = create_queue(queue_settings=queue_settings, receive_callback=receive_callback)
    queue.connect()
    print " [*] Waiting for events. To exit press CTRL+C"
    queue.receive()

if __name__ == '__main__':
    main()
