import datetime

from http import HTTPStatus
from unittest.mock import patch

from server.services.transaction_history import TransactionDto


BASE_URI = '/api/history/transactions/'
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



@patch('server.controllers.transaction.TransactionHistoryHandler')
def test_get_egress_transaction(
        mock_transaction_history_handler,
        app_client
):
    mock_transaction_history_handler.fetch_transaction_history.return_value = [
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
    uri = f'{BASE_URI}{TRANSACTION_TYPE_EGRESS}'
    query_params = {
        'start': mock_start,
        'end': mock_end
    }
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.OK

@patch('server.controllers.transaction.TransactionHistoryHandler')
def test_get_ingress_transaction(
        mock_transaction_history_handler,
        app_client
):
    mock_transaction_history_handler.fetch_transaction_history.return_value = [
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
    # Remove the trailing slash from the URI to match the server's expected path
    uri = f'{BASE_URI}{TRANSACTION_TYPE_INGRESS}'
    query_params = {
        'start': mock_start,
        'end': mock_end
    }
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.OK