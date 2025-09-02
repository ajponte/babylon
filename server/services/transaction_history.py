from server.db import get_session



class TransactionHistoryHandler:
    __slots__ = "_start", "_end", "_history"
    def __init__(self, *, start: int, end: int):
        self._start: int = start
        self._end: int = end
        self._history = []

    def fetch_transaction_history(self) -> list:
        return self._history
