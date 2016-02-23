from domain_events.rabbitmq_transport import Transport, DEFAULT_CONNECTION_SETTINGS


def get_transport():
    transport = Transport(exchange='test_exchange', connection_settings=DEFAULT_CONNECTION_SETTINGS)
    transport.connect()
    return transport


def test_send():
    transport = get_transport()
    transport.send('test message', 'x.y')
