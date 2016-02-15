#!/usr/bin/env python

import pika
import sys

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='domain-events', exchange_type='topic')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    print "queue_name is", queue_name

    binding_keys = sys.argv[1:]
    if not binding_keys:
        sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
        sys.exit(1)
    for routing_key in binding_keys:
        channel.queue_bind(exchange='domain-events', queue=queue_name, routing_key=routing_key)

    print " [*] Waiting for events. To exit press CTRL+C"

    def callback(ch, method, properties, body):
        print " [x] %r:%r" % (method.routing_key, body)

    channel.basic_consume(callback, queue=queue_name, no_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()
