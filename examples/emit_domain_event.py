#!/usr/bin/env python

import pika
import sys

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='domain-events', type='topic')

    routing_key = sys.argv[1]

    message = "hello world!"
    channel.basic_publish(exchange='domain-events', routing_key=routing_key, body=message)
    print " [x] Sent %r" % message
    connection.close()

if __name__ == '__main__':
    main()
