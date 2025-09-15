from datetime import date
from server.models import EgressTransactionSource
from server.models.egress_transaction import EgressTransaction


def test_create_and_retrieve_egress_transaction(db_session):
    # Create a new transaction
    new_transaction = EgressTransaction(
        date_posted=date(2025, 1, 15),
        source=EgressTransactionSource.CARD_PAYMENT,
        description="Groceries",
        amount=15000,
    )
    db_session.add(new_transaction)
    db_session.commit()

    # Retrieve the transaction by ID and check its values
    retrieved_tx = EgressTransaction.get_transaction_by_id(new_transaction.id, db_session)
    assert retrieved_tx is not None
    assert retrieved_tx.description == "Groceries"
    assert retrieved_tx.amount == 15000
    assert retrieved_tx.date_posted == date(2025, 1, 15)

def test_get_nonexistent_transaction(db_session):
    # Test getting a transaction that doesn't exist
    non_existent_tx = EgressTransaction.get_transaction_by_id("non-existent-id", db_session)
    assert non_existent_tx is None

def test_get_transactions_posted_within_bounds(db_session):
    # Add multiple transactions with different dates
    tx1 = EgressTransaction(
        date_posted=date(2025, 1, 1),
        source=EgressTransactionSource.CARD_PAYMENT,
        description="Rent",
        amount=100000,
    )
    tx2 = EgressTransaction(
        date_posted=date(2025, 1, 10),
        source=EgressTransactionSource.ONLINE_TRANSFER,
        description="Savings",
        amount=50000,
    )
    tx3 = EgressTransaction(
        date_posted=date(2025, 2, 5),
        source=EgressTransactionSource.ATM_WITHDRAWAL,
        description="Utilities",
        amount=7500,
    )
    db_session.add_all([tx1, tx2, tx3])
    db_session.commit()

    # Query for transactions within a specific date range
    start_date = date(2025, 1, 1)
    end_date = date(2025, 1, 31)
    results = EgressTransaction.get_transactions_posted_within_bounds(
        start_date, end_date, db_session
    )

    # Assert that only the expected transactions are returned
    assert len(results) == 2
    assert any(tx.description == "Rent" for tx in results)
    assert any(tx.description == "Savings" for tx in results)
    assert not any(tx.description == "Utilities" for tx in results)
