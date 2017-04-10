from domain_events import transport


def test_send():
    sender = transport.Sender(exchange='test_exchange')
    sender.send('test message', 'x.y')
    sender.disconnect()
