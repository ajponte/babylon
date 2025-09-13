"""Transactions controller."""

import logging
from http import HTTPStatus
from dataclasses import asdict
from typing import Any

from server.services.transaction_history import TransactionHistoryHandler


async def transaction_history(
    transaction_type, start: int, end: int
) -> tuple[dict[str, Any], int]:
    """
    Fetch transaction history between start and end.

    :param transaction_type: Type of transactions (ingress/egress).
    :param start: Start UTC epoch.
    :param end: End UTC epoch.
    :return: Tuple of Transaction history and status code.
    """
    if start >= end:
        message = f"{start} >= {end}"
        return {"message": message}, HTTPStatus.BAD_REQUEST
    try:
        logging.debug(f"Fetching transaction between {start} and {end}")
        resp = _transaction_search(transaction_type, start, end)
        return {"transactions": resp}, HTTPStatus.OK
    except Exception as e:
        message = f"Unknown exception while fetching transaction history between {start}, {end}."
        logging.info(message, exc_info=e)
        return {"message": message}, HTTPStatus.INTERNAL_SERVER_ERROR


def _transaction_search(transaction_type: str, start: int, end: int):
    """
    Search for transactions.

    :param transaction_type: Transaction type.
    :param start: Start UTC.
    :param end: End UTC.
    :return: Any transactions within the bounds.
    """
    handler = TransactionHistoryHandler(
        transaction_type=transaction_type, start=start, end=end
    )
    history = handler.fetch_transaction_history()
    return [asdict(h) for h in history]


# pylint: disable=unused-argument
async def transaction_get_by_id(transaction_id: str) -> tuple[dict, int]:
    """
    Fetch a transaction by its ID.

    :param transaction_id: Transaction ID.
    :return: Transaction entity.
    """
    # todo
    return {}, HTTPStatus.OK
