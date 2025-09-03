import logging
from http import HTTPStatus
from typing import Any

from server.services.transaction_history import TransactionHistoryHandler


async def transaction_history(start: int, end: int) -> tuple[dict[str, Any], int]:
    if not (start < end):
        message = f'{start} >= {end}'
        return {'message': message}, HTTPStatus.BAD_REQUEST
    try:
        logging.debug(f'Fetching transaction between {start} and {end}')
        resp = _transaction_search(start, end)
        return {'transactions': resp}, HTTPStatus.OK
    except Exception as e:
        message = f'Unknown exception while fetching transaction history between {start}, {end}.'
        logging.info(message, exc_info=e)
        return {'message': message}, HTTPStatus.INTERNAL_SERVER_ERROR

def _transaction_search(start: int, end: int):
    handler = TransactionHistoryHandler(start=start, end=end)
    return handler.fetch_transaction_history()
