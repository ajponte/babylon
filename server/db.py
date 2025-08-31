"""Database driver."""

import logging
from typing import Any
from flask import Flask, g
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

DATABASE_EXTENSION_KEY = "db"
SESSION_APP_CTX_KEY = "_session"


class Database:
    """Database Driver."""

    def __init__(self, config: dict[str, Any], sqlalchemy_base):
        """
        Constructor.

        :param config: DB Connection configs.
        :param sqlalchemy_base: SQLAlchemy Base.
        """
        database_url = config["SQLALCHEMY_DATABASE_URL"]
        # Determines how often (in seconds) the connection pool should refresh.
        pool_recycle = config["SQLALCHEMY_POOL_RECYCLE"]
        self._engine = create_engine(url=database_url, pool_recycle=pool_recycle)
        # Bind a new session to the engine.
        self._session = sessionmaker(bind=self._engine)
        self._base = sqlalchemy_base

    def create_tables(self):
        """Create DB tables if they don't exist."""
        self._base.metadata.create_all(self._engine)

    def attach_to_flask_app(self, flask_app: Flask, create_tables: bool = False):
        """
        Attach a Flask app instance to this database driver.

        :param create_tables: If true, create all tables from the schemas.
        """
        if create_tables:
            self.create_tables()
            self._engine.dispose()

        flask_app.extensions[DATABASE_EXTENSION_KEY] = self

    def get_session(self) -> Session:
        """
        Fetch an existing session, which can only be tied to a variable
        in the Flask App's global namespace. If no such session variable
        exists, create a new session, and cache the binding.

        :return: An existing SQLAlchemy session, or a newly created one.
        """
        session = g.get(SESSION_APP_CTX_KEY, None)
        if not session:
            logging.info("No session object cached. Creating a new one")
            session = sessionmaker(bind=self._engine)

        return session
