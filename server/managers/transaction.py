from dataclasses import asdict

from server.services.transaction_history import TransactionHistoryHandler, TransactionReadHandler


def transaction_fetch_by_id(
    transaction_id: str,
    transaction_type: str
) -> dict | None:
    """
    Return any transaction by ID.

    :param transaction_id: Transaction ID.
    :param transaction_type: Transaction type.
    :return: Transaction.
    """
    handler = TransactionReadHandler(
        transaction_id=transaction_id,
        transaction_type=transaction_type
    )
    return handler.read_transaction()



def transaction_search(
    transaction_type: str, start: int, end: int
):
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
