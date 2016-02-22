from domain_events.rabbitmq_transport import BaseQueue, DEFAULT_CONNECTION_SETTINGS, QueueSettings


def get_queue(is_receiver, binding_keys=None, queue_name='test_queue', queue_type=BaseQueue):
    queue_settings = QueueSettings(
        name=queue_name,
        is_receiver=is_receiver,
        exchange='test_exchange',
        binding_keys=binding_keys,
    )
    queue=queue_type(queue_settings, DEFAULT_CONNECTION_SETTINGS)
    queue.connect()

    return queue


def test_queue_creation_and_connection():
    queue = get_queue(False)
    queue.send('test message', 'x.y')
