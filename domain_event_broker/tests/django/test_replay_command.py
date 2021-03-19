from io import StringIO
from time import sleep
from django.core.management import call_command
from ..helpers import get_message_from_queue, get_queue_size


def test_replay(dead_letter_message):
    call_command('replay_domain_event', 'test-replay')
    sleep(.6)
    assert get_queue_size('test-replay-dl') == 0
    header, event = get_message_from_queue('test-replay')
    assert event.data == dead_letter_message


def test_interactive_replay(dead_letter_message, monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO('Replay'))
    output = StringIO()
    call_command('replay_domain_event', 'test-replay', '--interactive',
                 stdout=output)
    sleep(.6)
    assert get_queue_size('test-replay-dl') == 0
    header, event = get_message_from_queue('test-replay')
    assert event.data == dead_letter_message
    # Check JSON body is pretty-printed and sorted
    output_lines = output.getvalue().split('\n')
    assert output_lines[:3] == [
        'Please specify action for:',
        '{',
        '    "data": {'
    ]


def test_interactive_replay_leave(dead_letter_message, monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO('Leave'))
    call_command('replay_domain_event', 'test-replay', '--interactive')
    sleep(.6)
    assert get_queue_size('test-replay-dl') == 1
    assert get_queue_size('test-replay') == 0


def test_interactive_replay_discard(dead_letter_message, monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO('Discard'))
    call_command('replay_domain_event', 'test-replay', '--interactive')
    sleep(.6)
    assert get_queue_size('test-replay-dl') == 0
    assert get_queue_size('test-replay') == 0
