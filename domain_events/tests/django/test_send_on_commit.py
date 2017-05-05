from mock import patch
from django.db import transaction
from django.test.testcases import TransactionTestCase
from django.test.utils import override_settings

from domain_events.django import send_on_commit


@override_settings(DOMAIN_EVENT_PRODUCER_BROKER='amqp://guest:guest@localhost:5672')
class DomainEventTests(TransactionTestCase):

    @patch('domain_events.django.transaction.send_domain_event')
    def test_emit_no_transaction(self, send_mock):
        send_on_commit('test.no_transaction', {})
        send_mock.assert_called_with('test.no_transaction', {})

    @patch('domain_events.django.transaction.send_domain_event')
    def test_emit_on_commit(self, send_mock):
        with transaction.atomic():
            send_on_commit('test.commit', {})
            self.assertFalse(send_mock.called)
        send_mock.assert_called_with('test.commit', {})

    @patch('domain_events.django.transaction.send_domain_event')
    def test_discard_on_rollback(self, send_mock):
        try:
            with transaction.atomic():
                send_on_commit('test.rollback', {})
                raise Exception('Rollback transaction')
        except:
            pass
        self.assertFalse(send_mock.called)
        # Also don't emit event in subsequent transaction
        with transaction.atomic():
            pass
        self.assertFalse(send_mock.called)
