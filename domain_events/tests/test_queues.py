from domain_events import transport


def test_send():
    transport.Sender(exchange='test_exchange').send('test message', 'x.y')


def test_reconfigure_sender():
    transport.get_sender()
    original_settings = transport._connection_settings
    try:
        transport.configure('amqp://john:doe@localhost:5672')
        assert transport.get_sender().connection_settings == 'amqp://john:doe@localhost:5672'
    finally:
        transport.configure(original_settings)
