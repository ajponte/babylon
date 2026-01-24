"""Methods for managing transaction logic."""

import logging
from dataclasses import asdict
from datetime import date, datetime

from server.services.transaction_history import (
    TransactionHistoryHandler,
    TransactionReadHandler,
    TransactionPersister,
)

_LOGGER = logging.getLogger()


def transaction_fetch_by_id(transaction_id: str, transaction_type: str) -> dict | None:
    """
    Return any transaction by ID.

    :param transaction_id: Transaction ID.
    :param transaction_type: Transaction type.
    :return: Transaction.
    """
    handler = TransactionReadHandler(
        transaction_id=transaction_id, transaction_type=transaction_type
    )
    tx = handler.read_transaction()
    return asdict(tx) if tx else None


def transaction_search(transaction_type: str, start: int, end: int):
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


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def create_transaction(
    transaction_type: str,
    transaction_source: str,
    date_posted: date | str,
    amount: float,
    description: str,
    slip_number: str | str,
) -> str:
    """
    Create new transaction record.

    :param transaction_type: Transaction type.
    :param transaction_source: Transaction source.
    :param date_posted: Date posted.
    :param amount: Amount posted.
    :param description: Description.
    :param slip_number: Optional slip number.
    :return: The ID of the newly created transaction.
    """
    persister = TransactionPersister(transaction_type=transaction_type)
    if isinstance(date_posted, str):
        _LOGGER.info(
            "datePosted is a string. Converting to a format this server understands"
        )
        format_string = "%Y-%m-%d"
        date_posted = datetime.strptime(date_posted, format_string)
    return persister.create_transaction(
        source=transaction_source,
        date_posted=date_posted,
        amount=amount,
        description=description,
        slip_number=slip_number,
    )
