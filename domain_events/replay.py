from .transport import get_sender


RETRY = 'retry'
LEAVE = 'leave'
DISCARD = 'discard'


def default_message_callback(**kwargs):
    return RETRY


def replay(queue_name, message_callback=default_message_callback):
    retry_exchange = queue_name + '-retry'
    dead_letter_queue = queue_name + '-dl'
    transport = get_sender()
    transport.connect()
    frame, header, body = transport.channel.basic_get(dead_letter_queue)
    action = message_callback(frame=frame, header=header, body=body)
    if action == RETRY:
        transport.channel.basic_publish(exchange=retry_exchange,
                                        routing_key=frame.routing_key,
                                        body=body,
                                        )
        transport.channel.basic_ack(frame.delivery_tag)
    elif action == DISCARD:
        transport.channel.basic_ack(frame.delivery_tag)
    elif action == LEAVE:
        transport.channel.basic_reject(frame.delivery_tag, requeue=True)
    else:
        transport.channel.basic_reject(frame.delivery_tag, requeue=True)
        raise Exception("Invalid action '{}'".format(action))
    return frame.message_count


def replay_all(queue_name, message_callback=default_message_callback):
    """
    Replay all messages from the dead-letter queue.
    Return number of messages dead-lettered since starting the replay
    """
    count = replay(queue_name)
    for _ in range(count):
        remainder = replay(queue_name, message_callback)
    return remainder
