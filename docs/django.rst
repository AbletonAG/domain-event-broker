Django Integration
==================

Configuration
-------------

This library can be configured via your Django settings. Add
*domain_events.django* to your ``INSTALLED_APPS`` and set the
``DOMAIN_EVENT_BROKER`` in your settings:

    INSTALLED_APPS = (
        'domain_events.django',
        )

    DOMAIN_EVENT_BROKER = 'amqp://user:password@rabbitmq-host/domain-events'

Setting ``DOMAIN_EVENT_BROKER`` to ``None`` will deactivate communication with
RabbitMQ -- essentially disabling domain event routing. This can be useful in
development and test environments where RabbitMQ is not available.

Database transactions
---------------------

Domain events are published immediately. When emitting domain events from within a
database transaction, it's recommended to defer publishing until the transaction
is committed. Using a commit hook avoids spurious domain events if a
transaction is rolled back after an error.

We recommend using ``publish_on_commit`` instead of using
``publish_domain_event`` when you're using Django.

.. autofunction:: domain_events.django.publish_on_commit

Testing
-------

If you want to test a component in isolation that is publishing domain events,
we recommend mocking ``publish_domain_event`` or ``publish_on_commit``. For
testing subscribers, you can create ``DomainEvent`` objects manually and
directly call the handler function.

Replaying dead-lettered domain events
-------------------------------------

If an event couldn't be processed by an event handler it will end up in a
dead-letter queue. There's a Django management command that helps you
reschedule processing of dead-lettered events::

    django-admin replay_domain_event <handler-name>

The name is the one given to ``Subscriber.register``. The name is also used as
the queue name. If an event is dead lettered into
``user-registeration-confirmation-dl``, you'd call ``replay_domain_event
user-registration-confirmation``.
