# pylint: disable=too-few-public-methods, unused-import
"""Transaction History service object."""
from server.db import get_session


class TransactionHistoryHandler:
    """
    Service object for fetching transaction history.
    """

    __slots__ = "_transaction_type", "_start", "_end", "_history"

    def __init__(self, *, transaction_type: str, start: int, end: int):
        """
        Constructor.

        :param transaction_type: Transaction type.
        :param start: Start UTC
        :param end: End UTC.
        """
        self._transaction_type = transaction_type
        self._start: int = start
        self._end: int = end
        self._history: list = []

    def fetch_transaction_history(self) -> list:
        """Return any transaction history."""
        return self._history
