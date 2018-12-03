import pika
from domain_event_broker import DomainEvent


def get_queue_size(name, **kwargs):
    connection = pika.BlockingConnection()
    channel = connection.channel()
    q = channel.queue_declare(name, passive=True, **kwargs)
    count = q.method.message_count
    connection.close()
    return count


def check_queue_exists(name, **kwargs):
    connection = pika.BlockingConnection()
    channel = connection.channel()
    try:
        channel.queue_declare(name, passive=True, **kwargs)
    except pika.exceptions.ChannelClosed as error:
        connection.close()
        return error.args[0] != 404
    else:
        connection.close()
        return True


def get_message_from_queue(name, **kwargs):
    connection = pika.BlockingConnection()
    channel = connection.channel()
    method_frame, header, body = channel.basic_get(name)
    if method_frame:
        channel.basic_ack(method_frame.delivery_tag)
        event = DomainEvent.from_json(body)
        return header, event
    else:
        return None, None
