from domain_events.transport import Transport


def get_transport():
    transport = Transport(exchange='test_exchange')
    return transport


def test_send():
    transport = get_transport()
    transport.send('test message', 'x.y')
