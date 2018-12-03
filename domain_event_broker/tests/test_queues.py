from domain_event_broker import transport


def test_publish():
    publisher = transport.Publisher(exchange='test_exchange')
    publisher.publish('test message', 'x.y')
    publisher.disconnect()
