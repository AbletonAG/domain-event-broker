#!/usr/bin/env python

import sys

from domain_events import receive_domain_events


def handler(event):
    raise Exception("I can't handle that.")


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    receive_domain_events(handler, name='stumbling-steve', binding_keys=binding_keys, dead_letter=True)
