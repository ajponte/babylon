"""Shared SQLAlchemy base and methods."""

from enum import Enum
import uuid

from sqlalchemy.ext.declarative import declarative_base


BASE = declarative_base()


class EgressTransactionSource(Enum):
    """The source of a transaction."""

    CHASE = "CHASE"


class IngressTransactionSource(Enum):
    """The source of a transaction."""

    PAYROLL = "PAYROLL"


def create_random_uuid_hex() -> str:
    """Returns a randomly generated UUID in hex format."""
    return uuid.uuid4().hex
