import datetime
import json

from http import HTTPStatus
from unittest.mock import patch, MagicMock

import pytest

from server.services.transaction_history import TransactionDto
from tests.conftest import app_client

BASE_URI_TRANSACTIONS = '/api/history/transactions'
BASE_URI_TRANSACTION = '/api/history/transaction'
HTTP_HEADER_CONTENT_TYPE = 'application/json'


MOCK_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


TRANSACTION_TYPE_EGRESS = 'egress'
TRANSACTION_TYPE_INGRESS = 'ingress'

MOCK_EGRESS_TRANSACTION_ID = "b4077d29-c5a4-4e39-9d94-c37a86e5ecb2"
MOCK_INGRESS_TRANSACTION_ID = "53c549c8-7bfa-4f51-9be3-bcbbaaad9d10"

MOCK_DATE_POSTED = datetime.date(
    year=2025, month=9, day=8
)
MOCK_AMOUNT = 4532
MOCK_DESCRIPTION = "some description"
MOCK_EGRESS_SOURCE = "ATM_WITHDRAWAL"
MOCK_INGRESS_SOURCE = "INVESTMENT"


@patch('server.managers.transaction.TransactionHistoryHandler')
def test_get_egress_transaction(
        mock_transaction_history_handler,
        app_client
):
    mock_handler_instance = mock_transaction_history_handler.return_value
    mock_handler_instance.fetch_transaction_history.return_value = [
        TransactionDto(
            id=MOCK_EGRESS_TRANSACTION_ID,
            transaction_type=TRANSACTION_TYPE_EGRESS,
            date_posted=MOCK_DATE_POSTED,
            amount=MOCK_AMOUNT,
            source=MOCK_EGRESS_SOURCE,
            description=MOCK_DESCRIPTION
        )
    ]
    mock_start = 1757370903
    mock_end = 1757457303
    # Remove the trailing slash from the URI to match the server's expected path
    uri = f'{BASE_URI_TRANSACTIONS}/{TRANSACTION_TYPE_EGRESS}'
    query_params = {
        'start': mock_start,
        'end': mock_end
    }
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.OK

@patch('server.managers.transaction.TransactionHistoryHandler')
def test_get_ingress_transaction(
        mock_transaction_history_handler,
        app_client
):
    mock_handler_instance = mock_transaction_history_handler.return_value
    mock_handler_instance.fetch_transaction_history.return_value = [
        TransactionDto(
            id=MOCK_INGRESS_TRANSACTION_ID,
            transaction_type=TRANSACTION_TYPE_INGRESS,
            date_posted=MOCK_DATE_POSTED,
            amount=MOCK_AMOUNT,
            source=MOCK_INGRESS_SOURCE,
            description=MOCK_DESCRIPTION
        )
    ]
    mock_start = 1757370903
    mock_end = 1757457303
    uri = f'{BASE_URI_TRANSACTIONS}/{TRANSACTION_TYPE_INGRESS}'
    query_params = {
        'start': mock_start,
        'end': mock_end
    }
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.OK

@patch('server.managers.transaction.TransactionReadHandler')
def test_transaction_get_by_id(mock_transaction_read_handler, app_client):
    mock_handler_instance = mock_transaction_read_handler.return_value
    mock_handler_instance.read_transaction.return_value = TransactionDto(
        id=MOCK_INGRESS_TRANSACTION_ID,
        transaction_type=TRANSACTION_TYPE_INGRESS,
        date_posted=MOCK_DATE_POSTED,
        amount=MOCK_AMOUNT,
        source=MOCK_INGRESS_SOURCE,
        description=MOCK_DESCRIPTION
    )

    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    query_params = {'transactionId': MOCK_EGRESS_TRANSACTION_ID, "transactionType": TRANSACTION_TYPE_INGRESS}
    uri = f'{BASE_URI_TRANSACTION}'
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.OK
    transaction = resp.json()
    assert transaction['id'] == MOCK_INGRESS_TRANSACTION_ID
    assert transaction['transaction_type'] == TRANSACTION_TYPE_INGRESS

@patch('server.managers.transaction.TransactionReadHandler')
def test_transaction_get_by_id_not_found(mock_transaction_read_handler, app_client):
    """Test that we return an HTTP 404 when no DAO is found."""
    mock_handler_instance = mock_transaction_read_handler.return_value
    mock_handler_instance.read_transaction.return_value = None
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    query_params = {'transactionId': MOCK_EGRESS_TRANSACTION_ID, "transactionType": TRANSACTION_TYPE_INGRESS}
    uri = f'{BASE_URI_TRANSACTION}'
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.NOT_FOUND


@patch('server.managers.transaction.TransactionPersister')
def test_transaction_put_ingress(mock_transaction_persister, app_client):
    """Test creating an ingress transaction"""
    mock_handler_instance = mock_transaction_persister.return_value
    mock_handler_instance.create_transaction.return_value = MOCK_INGRESS_TRANSACTION_ID
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    uri = f'{BASE_URI_TRANSACTION}'
    transaction_request_body = {
        'amount': MOCK_AMOUNT,
        'transactionSource': 'INVESTMENT',
        'description': MOCK_DESCRIPTION,
        'transactionType': TRANSACTION_TYPE_INGRESS,
        'datePosted': str(MOCK_DATE_POSTED)
    }
    resp = app_client.put(uri, headers=headers, data=json.dumps(transaction_request_body))
    assert resp.status_code == HTTPStatus.CREATED
    assert resp.json()['transactionId'] == MOCK_INGRESS_TRANSACTION_ID

@patch('server.managers.transaction.TransactionPersister')
def test_transaction_put_egress(mock_transaction_persister, app_client):
    """Test creating an egress transaction"""
    mock_handler_instance = mock_transaction_persister.return_value
    mock_handler_instance.create_transaction.return_value = MOCK_EGRESS_TRANSACTION_ID
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    uri = f'{BASE_URI_TRANSACTION}'
    transaction_request_body = {
        'amount': MOCK_AMOUNT,
        'transactionSource': 'ATM_WITHDRAWAL',
        'description': MOCK_DESCRIPTION,
        'transactionType': TRANSACTION_TYPE_EGRESS,
        'datePosted': str(MOCK_DATE_POSTED)
    }
    resp = app_client.put(uri, headers=headers, data=json.dumps(transaction_request_body))
    assert resp.status_code == HTTPStatus.CREATED
    assert resp.json()['transactionId'] == MOCK_EGRESS_TRANSACTION_ID

@patch('server.managers.transaction.TransactionPersister')
def test_transaction_put_egress_conflict(mock_transaction_persister, app_client):
    """Test that we raise a conflict status when no transaction ID was returned from the persister."""
    mock_handler_instance = mock_transaction_persister.return_value
    mock_handler_instance.create_transaction.return_value = None
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    uri = f'{BASE_URI_TRANSACTION}'
    transaction_request_body = {
        'amount': MOCK_AMOUNT,
        'transactionSource': 'ATM_WITHDRAWAL',
        'description': MOCK_DESCRIPTION,
        'transactionType': TRANSACTION_TYPE_EGRESS,
        'datePosted': str(MOCK_DATE_POSTED)
    }
    resp = app_client.put(uri, headers=headers, data=json.dumps(transaction_request_body))
    assert resp.status_code == HTTPStatus.CONFLICT
