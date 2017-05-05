import pytest
from mock import patch
from django.db import transaction

from domain_events.django import send_on_commit


@pytest.mark.django_db(transaction=True)
@patch('domain_events.django.transaction.send_domain_event')
def test_emit_no_transaction(send_mock):
    send_on_commit('test.no_transaction', {})
    send_mock.assert_called_with('test.no_transaction', {})


@pytest.mark.django_db(transaction=True)
@patch('domain_events.django.transaction.send_domain_event')
def test_emit_on_commit(send_mock):
    with transaction.atomic():
        send_on_commit('test.commit', {})
        assert not send_mock.called
    send_mock.assert_called_with('test.commit', {})


@pytest.mark.django_db(transaction=True)
@patch('domain_events.django.transaction.send_domain_event')
def test_discard_on_rollback(send_mock):
    try:
        with transaction.atomic():
            send_on_commit('test.rollback', {})
            raise Exception('Rollback transaction')
    except:
        pass
    assert not send_mock.called
    # Also don't emit event in subsequent transaction
    with transaction.atomic():
        pass
    assert not send_mock.called
