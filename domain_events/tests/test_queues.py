from domain_events.transport import Sender, get_sender, configure


def test_send():
    Sender(exchange='test_exchange').send('test message', 'x.y')


def test_reconfigure_sender():
    get_sender()
    configure('amqp://john:doe@localhost:5672')
    assert get_sender().connection_settings == 'amqp://john:doe@localhost:5672'
