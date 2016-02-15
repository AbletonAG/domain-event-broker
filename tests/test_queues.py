from abl.util import Bunch
from domain_events.rabbitmq_transport import RabbitQueue, DummyQueue

def get_queue(is_receiver, binding_keys=None, queue_name='test_queue', queue_type=DummyQueue):
    queue_settings = Bunch(
        NAME=queue_name,
        IS_RECEIVER=is_receiver,
        EXCHANGE='test_exchange',
        EXCHANGE_TYPE='topic',
        BINDING_KEYS=binding_keys,
        DURABLE=True,
        DLX=False,
    )
    connection_settings = Bunch(
        RABBITMQ_HOST='localhost',
        RABBITMQ_PORT=None,
        RABBITMQ_USER=None,
        RABBITMQ_PW=None,
    )
    queue=queue_type(queue_settings, connection_settings)
    queue.connect()

    return queue


def test_queue_creation_and_connection():
    queue = get_queue(False)
    queue.send('test message', 'x.y')
