"""Transactions controller."""

import logging
from http import HTTPStatus
from typing import Any

import connexion

from server.managers.transaction import (
    transaction_search,
    transaction_fetch_by_id,
    create_transaction,
)

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


async def transaction_put() -> tuple[dict[str, str], int]:
    """
    Create a new transaction.

    :return: Tuple, which upon a successful operation, contains the transaction ID.
    """
    payload = await connexion.request.json()
    transaction_type = payload["transactionType"]
    transaction_source = payload["transactionSource"]
    date_posted = payload["datePosted"]
    amount = payload["amount"]
    description = payload["description"]
    slip_number = payload.get("slipNumber")

    try:
        _LOGGER.debug(
            f"Sending request to persister to create a {transaction_type} transaction"
        )
        transaction_id = create_transaction(
            transaction_type=transaction_type,
            transaction_source=transaction_source,
            date_posted=date_posted,
            amount=amount,
            description=description,
            slip_number=slip_number,
        )
        if not transaction_id:
            message = "No transaction ID returned from creating."
            _LOGGER.info(message)
            return {"message": message}, HTTPStatus.CONFLICT
        return {"transactionId": transaction_id}, HTTPStatus.CREATED
    except Exception as e:
        message = f"Unknown exception while creating transaction. Error: {e}"
        _LOGGER.debug(message)
        return {"message": message}, HTTPStatus.INTERNAL_SERVER_ERROR
