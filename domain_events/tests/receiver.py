#!/usr/bin/env python

import sys
from .test_queues import get_queue

queue_name, binding_key = sys.argv[1:]

queue = get_queue(True, binding_keys=[binding_key], queue_name=queue_name)
queue.receive()
