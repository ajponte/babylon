from server.db import get_session

class TransactionHistoryHandler:
    __slots__ = "_transaction_type", "_start", "_end", "_history"
    def __init__(
        self,
        *,
        transaction_type: str,
        start: int,
        end: int
    ):
        self._transaction_type = transaction_type
        self._start: int = start
        self._end: int = end
        self._history = []

    def fetch_transaction_history(self) -> list:
        return self._history
