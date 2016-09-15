from .transport import get_sender


def replay(dead_letter_queue, retry_exchange):
    # TODO: all queues with a dead-letter queue need a retry exchange for this to work
    transport = get_sender()
    transport.connect()
    frame, header, body = transport.channel.basic_get(dead_letter_queue)
    if transport.basic_publish(exchange=retry_exchange,
                               routing_key=frame.routing_key,
                               body=body,
                               ): # TODO: when is this false?
        transport.channel.basic_ack(frame.delivery_tag)
    else:
        # TODO: nack will keep the message at the head of the queue
        transport.channel.basic_nack(frame.delivery_tag)
    # TODO: return success?
    return frame.message_count


def replay_all(dead_letter_queue, retry_exchange):
    """
    Replay all messages from the dead-letter queue.
    Return number of messages dead-lettered since starting the replay
    """
    count = replay(dead_letter_queue, retry_exchange)
    for _ in range(count):
        remainder = replay(dead_letter_queue, retry_exchange)
    return remainder
