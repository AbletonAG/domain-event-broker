#!/usr/bin/env python

import sys

from domain_events import Receiver


def handler(event):
    raise Exception("I can't handle that.")


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    receiver = Receiver()
    receiver.register(handler, name='stumbling-steve', binding_keys=binding_keys, dead_letter=True)
    receiver.start_consuming()
