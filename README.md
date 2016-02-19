Getting Started
---------------

Make sure you have rabbitmq installed locally for testing.

* create virtualenv and activate it
* run `pip install -r requirements.txt -r dev_requirements.txt -e .`
* the only external dependency (so far) is `pika>=0.9.13`


Architecture
------------

This module defines everything that's needed to use Domain Events (at Ableton).
There's

* the transport, currently done via rabbitmq: `domain_events.queue`. This should be usable independend of the events.
* generic domain events: `domain_events.event`
* ableton specific domain events: TBC (there might be a more lightweight way to share domain event specification that by sharing a module?)

Testing
-------

testing is currently done by `py.test` which allows some quite advanced testing features.
