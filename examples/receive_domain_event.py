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
    name, binding_key = sys.argv[1:]

    queue_settings = QueueSettings(
        name=name,
        is_receiver=True,
        binding_keys=(binding_key,),
    )

    def receive_callback(ch, method, properties, body):
        print " [x] %r:%r" % (method.routing_key, body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    queue = create_queue(queue_settings=queue_settings, receive_callback=receive_callback)
    queue.connect()
    print " [*] Waiting for events. To exit press CTRL+C"
    queue.receive()

if __name__ == '__main__':
    main()
