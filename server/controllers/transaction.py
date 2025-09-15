"""Transactions controller."""

import logging
from http import HTTPStatus
from typing import Any

from server.managers.transaction import transaction_search, transaction_fetch_by_id

_LOGGER = logging.getLogger()


async def transaction_history(
    transaction_type, start: int, end: int
) -> tuple[dict[str, Any] | None, int]:
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
        resp = transaction_search(transaction_type, start, end)
        return {"transactions": resp}, HTTPStatus.OK
    except Exception as e:
        message = f"Unknown exception while fetching transaction history between {start}, {end}."
        logging.info(message, exc_info=e)
        return {"message": message}, HTTPStatus.INTERNAL_SERVER_ERROR


# pylint: disable=unused-argument
async def transaction_get_by_id(
    transaction_id: str, transaction_type: str
) -> tuple[dict[str, Any] | None, int]:
    """
    Fetch a transaction by its ID.

    :param transaction_id: Transaction ID.
    :param transaction_type: Type of transactions (ingress/egress).
    :return: Transaction entity.
    """
    try:
        result = transaction_fetch_by_id(
            transaction_id=transaction_id, transaction_type=transaction_type
        )
        if not result:
            message = f"No result returned for transaction {transaction_id}"
            _LOGGER.debug(message)
            return {"message": message}, HTTPStatus.NOT_FOUND
        _LOGGER.debug(f"Result successfully returned for transaction {transaction_id}")
        return result, HTTPStatus.OK
    except Exception as e:
        message = f"Error fetching {transaction_type} transaction. Error: {e}"
        _LOGGER.debug(message)
        return {"message": message}, HTTPStatus.INTERNAL_SERVER_ERROR
