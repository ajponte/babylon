# pylint: disable=too-few-public-methods
"""Represents ingress, (money in) from a specific account."""
import logging
from typing import Optional
from datetime import datetime, date

from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.types import Enum, Text, String, Integer
from server.models import BASE, create_random_uuid_hex, IngressTransactionSource


class IngressTransaction(BASE):
    """IngressTransaction ORM mapper."""

    __tablename__ = "inress_transaction"
    id: Mapped[str] = mapped_column(primary_key=True, default=create_random_uuid_hex)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    date_updated: Mapped[datetime] = mapped_column(default=datetime.now())
    date_posted: Mapped[date] = mapped_column(nullable=False)

    source = mapped_column(Enum(IngressTransactionSource), nullable=False)

    description: Mapped[str] = mapped_column(String(30), nullable=False)

    slip_number: Optional[Mapped[str]] = mapped_column(Text)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    @classmethod
    def get_transaction_by_id(cls, tx_id: str, session: Session):
        """
        Return any transactions by ID.

        :param tx_id: ID
        :param session: SQLAlchemy Session.
        :return: The transaction, or null
        """
        inress_tx = session.get(cls, cls.id == tx_id).one_or_none()  # type: ignore
        logging.debug(f"results for ingress: {inress_tx}")
        return inress_tx
