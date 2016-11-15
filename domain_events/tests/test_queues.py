from domain_events import transport


def test_send():
    sender = transport.Sender(transport.DEFAULT_CONNECTION_SETTINGS, exchange='test_exchange')
    sender.send('test message', 'x.y')
    sender.disconnect()
