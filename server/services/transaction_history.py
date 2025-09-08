# pylint: disable=too-few-public-methods, unused-import
"""Transaction History service object."""
from enum import StrEnum
from dataclasses import dataclass
from datetime import date

from server.db import get_session
from server.date_utils import epoch_to_date_utc
from server.models.egress_transaction import EgressTransaction
from server.models.ingress_transaction import IngressTransaction


class TransactionType(StrEnum):
    """Transaction type enum."""

    INGRESS = "ingress"
    EGRESS = "egress"


@dataclass(frozen=True)
class TransactionDto:
    """Transaction DTO to convert from data objects to return to API."""

    id: str
    transaction_type: str
    date_posted: date
    source: str
    description: str
    amount: float
    slip_number: str | None = None


class TransactionHistoryHandler:
    """
    Service object for fetching transaction history.
    """

    def __init__(self, *, transaction_type: str, start: int, end: int):
        """
        Constructor.

        :param transaction_type: Transaction type.
        :param start: Start UTC
        :param end: End UTC.
        """
        self._transaction_type = TransactionType(transaction_type)
        self._start: date = epoch_to_date_utc(start)
        self._end: date = epoch_to_date_utc(end)

    def fetch_transaction_history(self) -> list[TransactionDto]:
        """Return any transaction history."""
        tx_dao = select_transaction_dao(self._transaction_type)
        results = tx_dao.get_transactions_posted_within_bounds(
            session=get_session(),
            start=self._start,
            end=self._end
        )
        return _from_transaction_dao(
            transactions=results,
            transaction_type=self._transaction_type
        )

def _from_transaction_dao(transactions: list, transaction_type: str) -> list[TransactionDto]:
    """Return a list of transaction DAO."""
    return [
        _to_transaction_dto(
            transaction=tx, transaction_type=transaction_type
        ) for tx in transactions
    ]

def _to_transaction_dto(transaction, transaction_type: str) -> TransactionDto:
    """Convert a sqlalchemy DAO to the appropriate DTO."""
    return TransactionDto(
        id=transaction.id,
        transaction_type=transaction_type,
        date_posted=transaction.date_posted,
        source=transaction.source.value,
        slip_number=transaction.slip_number,
        description=transaction.description,
        amount=transaction.amount,
    )

def select_transaction_dao(transaction_type: str):
    """Return the appropriate DAO."""
    if transaction_type == 'ingress':
        return IngressTransaction
    elif transaction_type == 'egress':
        return EgressTransaction
    raise ValueError(f'{transaction_type} is not valid')
