# pylint: disable=too-few-public-methods
"""Represents egress, (money out) from a specific account."""
import logging
from typing import Optional
from datetime import datetime, date
from sqlalchemy import and_
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, Text, String, Integer
from sqlalchemy.orm.session import Session
from server.models import BASE, create_random_uuid_hex, EgressTransactionSource

_LOGGER = logging.getLogger()


class EgressTransaction(BASE):
    """EgressTransaction ORM mapper."""

    __tablename__ = "egress_transaction"
    # workaround for https://docs.sqlalchemy.org/en/20/errors.html#error-zlpr
    __allow_unmapped__ = True
    id: Mapped[str] = mapped_column(primary_key=True, default=create_random_uuid_hex)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    date_updated: Mapped[datetime] = mapped_column(default=datetime.now())
    date_posted: Mapped[date] = mapped_column(nullable=False)

    source = mapped_column(Enum(EgressTransactionSource), nullable=False)

    description: Mapped[str] = mapped_column(String(30), nullable=False)

    slip_number: Optional[Mapped[str]] = mapped_column(Text)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    # For testing
    @classmethod
    def get_transactions(cls, session: Session):
        """
        For testing only.

        :param session: SQLAlchemy session.
        :return: All transactions.
        """
        return session.query(cls).all()

    @classmethod
    def get_transaction_by_id(cls, tx_id: str, session: Session):
        """
        Return any transactions by ID.

        :param tx_id: ID
        :param session: SQLAlchemy Session.
        :return: The transaction, or null
        """
        try:
            egress_tx = session.query(cls).filter(cls.id == tx_id).one_or_none()  # type: ignore
            _LOGGER.debug(f"results for egress: {egress_tx}")
            return egress_tx
        except Exception as e:
            _LOGGER.info(f"Error while fetching transaction {tx_id}")
            raise e

    @classmethod
    def get_transactions_posted_within_bounds(
        cls, start: date, end: date, session: Session
    ):
        """
        Return any transactions posted between START and END.

        :param start: Start dt.
        :param end: End dt.
        :param session: SQLAlchemy session.
        :return: List of transactions.
        """
        try:
            results = session.query(cls).filter(
                and_(cls.date_posted >= start, cls.date_posted <= end)
            )
            return results.all()
        except Exception as e:
            _LOGGER.info(f"Error while fetching transactions between {start}, {end}")
            raise e
