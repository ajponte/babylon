import uuid
import logging
import random
from typing import Optional
from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Date,
    DateTime,
    MetaData,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import Session, sessionmaker, registry
from sqlalchemy.types import Enum

from faker import Faker

from run_flask import (
    SQLALCHEMY_DB_ENGINE,
    SQLALCHEMY_DB_USER,
    SQLALCHEMY_DB_PASS,
    SQLALCHEMY_DB_HOST,
    SQLALCHEMY_DB_PORT,
    SQLALCHEMY_DATABASE_NAME,
)

# --- Database Setup and Model Definitions ---

# A simple function to create a random UUID in hexadecimal format.
def create_random_uuid_hex():
    """Generates a random UUID in hex format."""
    return uuid.uuid4().hex


# Define the Enums for transaction sources, since they were not provided.
class EgressTransactionSource(PyEnum):
    """Sources for outgoing money."""
    CARD_PAYMENT = 'CARD_PAYMENT'
    ONLINE_TRANSFER = 'ONLINE_TRANSFER'
    ATM_WITHDRAWAL = 'ATM_WITHDRAWAL'


class IngressTransactionSource(PyEnum):
    """Sources for incoming money."""
    SALARY = 'SALARY'
    INVESTMENT = 'INVESTMENT'
    REFUND = 'REFUND'


# Define the model classes first.
class EgressTransaction:
    """EgressTransaction ORM mapper."""

    def __init__(self, date_posted, source, description, amount, slip_number=None):
        self.id = create_random_uuid_hex()
        self.date_created = datetime.now()
        self.date_updated = datetime.now()
        self.date_posted = date_posted
        self.source = source
        self.description = description
        self.slip_number = slip_number
        self.amount = amount

    def __repr__(self):
        """String representation for easier debugging."""
        return (f"<EgressTransaction(id='{self.id}', description='{self.description}', "
                f"amount='{self.amount}', source='{self.source}', "
                f"date_posted='{self.date_posted}')>")


class IngressTransaction:
    """IngressTransaction ORM mapper."""

    def __init__(self, date_posted, source, description, amount, slip_number=None):
        self.id = create_random_uuid_hex()
        self.date_created = datetime.now()
        self.date_updated = datetime.now()
        self.date_posted = date_posted
        self.source = source
        self.description = description
        self.slip_number = slip_number
        self.amount = amount

    def __repr__(self):
        """String representation for easier debugging."""
        return (f"<IngressTransaction(id='{self.id}', description='{self.description}', "
                f"amount='{self.amount}', source='{self.source}', "
                f"date_posted='{self.date_posted}')>")


# --- Imperative Mapping ---
metadata = MetaData()
mapper_registry = registry()

egress_table = Table(
    "egress_transaction",
    metadata,
    Column('id', String(32), primary_key=True),
    Column('date_created', DateTime, default=datetime.now()),
    Column('date_updated', DateTime, default=datetime.now()),
    Column('date_posted', Date, nullable=False),
    Column('source', Enum(EgressTransactionSource), nullable=False),
    Column('description', String(32), nullable=False),
    Column('slip_number', Text),
    Column('amount', Integer, nullable=False)
)

ingress_table = Table(
    "ingress_transaction",
    metadata,
    Column('id', String(32), primary_key=True),
    Column('date_created', DateTime, default=datetime.now()),
    Column('date_updated', DateTime, default=datetime.now()),
    Column('date_posted', Date, nullable=False),
    Column('source', Enum(IngressTransactionSource), nullable=False),
    Column('description', String(32), nullable=False),
    Column('slip_number', Text),
    Column('amount', Integer, nullable=False)
)

mapper_registry.map_imperatively(EgressTransaction, egress_table)
mapper_registry.map_imperatively(IngressTransaction, ingress_table)


# --- Main Script ---
def main():
    """Generates mock data and loads it into the database."""
    driver: str = "psycopg2"

    sqlalchemy_url = f"{SQLALCHEMY_DB_ENGINE}+{driver}://{SQLALCHEMY_DB_USER}:{SQLALCHEMY_DB_PASS}@{SQLALCHEMY_DB_HOST}:{SQLALCHEMY_DB_PORT}/{SQLALCHEMY_DATABASE_NAME}"
    # Create an in-memory SQLite database.
    engine = create_engine(sqlalchemy_url)
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session: Session = Session()

    # Initialize Faker for generating mock data.
    fake = Faker()

    # Define the number of transactions to generate.
    num_transactions = 50

    egress_sources = list(EgressTransactionSource)
    ingress_sources = list(IngressTransactionSource)

    # Generate mock transactions.
    print(f"Generating {num_transactions} mock transactions...")
    transactions = []
    for _ in range(num_transactions):
        # Generate a random date within the last year.
        date_posted = fake.date_object()

        # Create a mock Egress transaction.
        egress_tx = EgressTransaction(
            date_posted=date_posted,
            source=random.choice(egress_sources),
            description=fake.sentence(nb_words=2),
            slip_number=fake.text(max_nb_chars=10) if random.random() > 0.5 else None,
            amount=random.randint(100, 5000)
        )
        transactions.append(egress_tx)

        # Create a mock Ingress transaction.
        ingress_tx = IngressTransaction(
            date_posted=date_posted,
            source=random.choice(ingress_sources),
            description=fake.sentence(nb_words=2),
            slip_number=fake.text(max_nb_chars=10) if random.random() > 0.5 else None,
            amount=random.randint(1000, 10000)
        )
        transactions.append(ingress_tx)

    # Add all transactions to the session and commit.
    try:
        session.add_all(transactions)
        session.commit()
        print("Mock data loaded successfully.")
    except Exception as e:
        print(f'Error loading mock data. {e}')
        session.rollback()

    # --- Verification and Query ---

    # Query and print the first 5 egress transactions.
    print("\n--- First 5 Egress Transactions ---")
    egress_results = session.query(EgressTransaction).limit(5).all()
    for tx in egress_results:
        print(tx)

    # Query and print the first 5 ingress transactions.
    print("\n--- First 5 Ingress Transactions ---")
    ingress_results = session.query(IngressTransaction).limit(5).all()
    for tx in ingress_results:
        print(tx)

    # Close the session.
    session.close()


if __name__ == "__main__":
    main()
