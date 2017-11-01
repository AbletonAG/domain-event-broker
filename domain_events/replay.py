from .transport import Transport
from . import settings


RETRY = 'retry'
LEAVE = 'leave'
DISCARD = 'discard'


def retry_event(**kwargs):
    return RETRY


def replay_event(queue_name, message_callback=retry_event,
                 connection_settings=settings.DEFAULT):
    """
    Move one domain event from a dead-letter queue back into the processing queue.

    :param str queue_name: Name of the queue where to move the event.
    :param function message_callback: A callable that receives the event and
        returns either ``RETRY``, ``LEAVE`` or ``DISCARD``.
    :param str connection_settings:

    :return: The number of messages left in the dead letter queue.
    :rtype: int
    """
    if connection_settings is None:
        return 0
    elif connection_settings is settings.DEFAULT:
        connection_settings = settings.BROKER
    retry_exchange = queue_name + '-retry'
    dead_letter_queue = queue_name + '-dl'
    transport = Transport(connection_settings)
    transport.connect()
    frame, header, body = transport.channel.basic_get(dead_letter_queue)
    if frame is None:
        return 0
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


def replay_all(queue_name, message_callback=retry_event,
               connection_settings=settings.DEFAULT):
    """
    Replay all messages currently in the dead-letter queue.
    Return number of messages dead-lettered since starting the replay.
    """
    remainder = replay_event(queue_name, message_callback, connection_settings=connection_settings)
    for _ in range(remainder):
        remainder = replay_event(queue_name, message_callback, connection_settings=connection_settings)
    return remainder
