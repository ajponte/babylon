from datetime import date
from server.models import IngressTransactionSource
from server.models.ingress_transaction import IngressTransaction


def test_create_and_retrieve_ingress_transaction(db_session):
    # Create a new transaction
    new_transaction = IngressTransaction(
        date_posted=date(2025, 1, 15),
        source=IngressTransactionSource.INVESTMENT,
        description="dividend",
        amount=15000,
    )
    db_session.add(new_transaction)
    db_session.commit()

    # Retrieve the transaction by ID and check its values
    retrieved_tx = IngressTransaction.get_transaction_by_id(new_transaction.id, db_session)
    assert retrieved_tx is not None
    assert retrieved_tx.description == "dividend"
    assert retrieved_tx.amount == 15000
    assert retrieved_tx.date_posted == date(2025, 1, 15)

def test_get_nonexistent_transaction(db_session):
    # Test getting a transaction that doesn't exist
    non_existent_tx = IngressTransaction.get_transaction_by_id("non-existent-id", db_session)
    assert non_existent_tx is None

def test_get_transactions_posted_within_bounds(db_session):
    # Add multiple transactions with different dates
    tx1 = IngressTransaction(
        date_posted=date(2025, 1, 1),
        source=IngressTransactionSource.SALARY,
        description="paycheck",
        amount=100000,
    )
    tx2 = IngressTransaction(
        date_posted=date(2025, 1, 10),
        source=IngressTransactionSource.REFUND,
        description="return item",
        amount=50000,
    )
    tx3 = IngressTransaction(
        date_posted=date(2025, 2, 5),
        source=IngressTransactionSource.INVESTMENT,
        description="dividend",
        amount=7500,
    )
    db_session.add_all([tx1, tx2, tx3])
    db_session.commit()

    # Query for transactions within a specific date range
    start_date = date(2025, 1, 1)
    end_date = date(2025, 1, 31)
    results = IngressTransaction.get_transactions_posted_within_bounds(
        start_date, end_date, db_session
    )

    # Assert that only the expected transactions are returned
    assert len(results) == 2
    assert any(tx.description == "paycheck" for tx in results)
    assert any(tx.description == "return item" for tx in results)
    assert not any(tx.description == "dividend" for tx in results)
