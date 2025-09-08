# pylint: disable=too-few-public-methods, unused-import
"""Transaction History service object."""
from enum import StrEnum
from dataclasses import dataclass
from datetime import date

from server.db import get_session
from server.models.ingress_transaction import IngressTransaction

class TransactionType(StrEnum):
    INGRESS = 'ingress'
    EGRESS = 'egress'

@dataclass(frozen=True)
class TransactionDto:
    id: str
    transaction_type: str
    date_posted: date
    source: str
    description: str
    slip_number: str | None
    amount: float

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
        self._start: int = start
        self._end: int = end

    def fetch_transaction_history(self) -> list[TransactionDto]:
        """Return any transaction history."""
        history: list[TransactionDto] = []
        if self._transaction_type == 'ingress':
            results = IngressTransaction.get_transactions(session=get_session())
            for result in results:
                history.append(
                    TransactionDto(
                        id=result.id,
                        transaction_type=self._transaction_type,
                        date_posted=result.date_posted,
                        source=result.source.value,
                        slip_number=result.slip_number,
                        description=result.description,
                        amount=result.amount
                    )
                )

        return history
