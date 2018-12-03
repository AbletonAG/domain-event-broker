import pytest
from mock import patch
from django.db import transaction

from domain_event_broker.django import publish_on_commit


@pytest.mark.django_db(transaction=True)
@patch('domain_event_broker.django.transaction.publish_domain_event')
def test_publish_no_transaction(publish_mock):
    publish_on_commit('test.no_transaction', {})
    publish_mock.assert_called_with('test.no_transaction', {})


@pytest.mark.django_db(transaction=True)
@patch('domain_event_broker.django.transaction.publish_domain_event')
def test_publish_on_commit(publish_mock):
    with transaction.atomic():
        publish_on_commit('test.commit', {})
        assert not publish_mock.called
    publish_mock.assert_called_with('test.commit', {})


class RollbackError(Exception):
    pass


@pytest.mark.django_db(transaction=True)
@patch('domain_event_broker.django.transaction.publish_domain_event')
def test_discard_on_rollback(publish_mock):
    try:
        with transaction.atomic():
            publish_on_commit('test.rollback', {})
            raise RollbackError('Rollback transaction')
    except RollbackError:
        pass
    assert not publish_mock.called
    # Also don't emit event in subsequent transaction
    with transaction.atomic():
        pass
    assert not publish_mock.called
