# pylint: disable=too-few-public-methods
"""Represents egress, (money out) from a specific account."""
import logging
from typing import Optional
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, Text, String, Integer
from sqlalchemy.orm.session import Session
from server.models import BASE, create_random_uuid_hex, EgressTransactionSource


class EgressTransaction(BASE):
    """EgressTransaction ORM mapper."""

    __tablename__ = "egress_transaction"
    id: Mapped[str] = mapped_column(primary_key=True, default=create_random_uuid_hex)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    date_updated: Mapped[datetime] = mapped_column(default=datetime.now())
    date_posted: Mapped[date] = mapped_column(nullable=False)

    source = mapped_column(Enum(EgressTransactionSource), nullable=False)

    description: Mapped[str] = mapped_column(String(30), nullable=False)

    slip_number: Optional[Mapped[str]] = mapped_column(Text)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    @classmethod
    def get_transaction_by_id(
        cls,
        id: str,
        session: Session
    ) -> list:
        """
        Return any transactions by ID.

        :param id: ID
        :param session: SQLAlchemy Session.
        :return: The transaction, or null
        """
        egress_tx = session.get(cls, id).all()
        return egress_tx
