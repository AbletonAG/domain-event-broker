from domain_events.transport import Sender


def test_send():
    Sender(exchange='test_exchange').send('test message', 'x.y')
