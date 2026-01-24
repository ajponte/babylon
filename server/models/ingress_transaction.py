# pylint: disable=too-few-public-methods
"""Represents ingress, (money in) from a specific account."""
import logging
from typing import Optional
from datetime import datetime, date

from sqlalchemy import and_
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.types import Enum, Text, String, Integer
from server.models import BASE, create_random_uuid_hex, IngressTransactionSource

_LOGGER = logging.getLogger()


class IngressTransaction(BASE):
    """IngressTransaction ORM mapper."""

    __tablename__ = "ingress_transaction"
    # workaround for https://docs.sqlalchemy.org/en/20/errors.html#error-zlpr
    __allow_unmapped__ = True
    id: Mapped[str] = mapped_column(primary_key=True, default=create_random_uuid_hex)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    date_updated: Mapped[datetime] = mapped_column(default=datetime.now())
    date_posted: Mapped[date] = mapped_column(nullable=False)

    source = mapped_column(Enum(IngressTransactionSource), nullable=False)

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
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def create_transaction(
        cls,
        transaction_source: str,
        date_posted: date,
        amount: float,
        description: str,
        slip_number: str | None,
        session: Session,
    ) -> str:
        """
        Create a new ingress transaction record.

        :param transaction_source: Transaction source.
        :param date_posted: Date posted.
        :param amount: Amount posted.
        :param description: Description.
        :param slip_number: Optional slip number.
        :param session: SQLAlchemy session.
        :return: The ID of the created record.
        """
        transaction = cls(
            date_posted=date_posted,
            amount=amount,
            source=IngressTransactionSource(transaction_source),
            description=description,
            slip_number=slip_number,
        )

        try:
            session.add(transaction)
            session.commit()
            return transaction.id
        except Exception as e:
            message = f"Error adding ingress object. Error: {e}"
            _LOGGER.info(message)
            _LOGGER.debug("Rolling back")
            session.rollback()
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

    @classmethod
    def get_transaction_by_id(cls, tx_id: str, session: Session):
        """
        Return any transactions by ID.

        :param tx_id: ID
        :param session: SQLAlchemy Session.
        :return: The transaction, or null
        """
        inress_tx = session.query(cls).filter(cls.id == tx_id).one_or_none()  # type: ignore
        logging.debug(f"results for ingress: {inress_tx}")
        return inress_tx
