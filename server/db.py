"""Database driver."""

import logging
from typing import Any
from flask import Flask, g, current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

DATABASE_EXTENSION_KEY = "db"
SESSION_APP_CTX_KEY = "_session"

_LOGGER = logging.getLogger()


class Database:
    """Database Driver."""

    def __init__(self, config: dict[str, Any], sqlalchemy_base):
        """
        Constructor.

        :param config: DB Connection configs.
        :param sqlalchemy_base: SQLAlchemy Base.
        """
        if "DATABASE_URL" in config: # Changed check from SQLALCHEMY_DATABASE_URL
            _database_url = config["DATABASE_URL"]
        else:
            _database_url = _make_sqlalchemy_url(
                engine=config["SQLALCHEMY_DB_ENGINE"],
                host=config["DB_HOST"],
                port=config["DB_PORT"],
                user=config["DB_USERNAME"],
                passwd=config["DB_PASSWORD"],
                database=config["SQLALCHEMY_DATABASE_NAME"],
            )
        # Determines how often (in seconds) the connection pool should refresh.
        pool_recycle = config["SQLALCHEMY_POOL_RECYCLE"]
        self._engine = create_engine(url=_database_url, pool_recycle=pool_recycle)
        self._session_maker = sessionmaker(bind=self._engine)
        self._base = sqlalchemy_base

    def create_tables(self):
        """Create DB tables if they don't exist."""
        self._base.metadata.create_all(self._engine)

    def attach_to_flask_app(self, flask_app: Flask, create_tables: bool = False):
        """
        Attach a Flask app instance to this database driver.

        :param flask_app: Created flask app.
        :param create_tables: If true, create all tables from the schemas.
        """
        # Bind a new session to the engine.
        session = sessionmaker(bind=self._engine)
        flask_app.extensions[SESSION_APP_CTX_KEY] = session()
        if create_tables:
            _LOGGER.debug("Creating tables from schema.")
            self.create_tables()
            _LOGGER.debug("Done creating tables from schema.")
            _LOGGER.debug("Disposing existing connection pool.")
            self._engine.dispose()
            _LOGGER.debug("Disposed connection pool.")
        flask_app.extensions[DATABASE_EXTENSION_KEY] = self

        @flask_app.teardown_appcontext
        def close_session(error=None):  # pylint: disable=unused-argument
            """
            Handler for cleaning up DB sessions.
            """
            session = getattr(g, SESSION_APP_CTX_KEY, None)
            if session is not None:
                _LOGGER.debug("Closing cached sqlalchemy session")
                session.close()


def get_session() -> Session:
    """
    Fetch an existing session, which can only be tied to a variable
    in the Flask App's global namespace. If no such session variable
    exists, create a new session, and cache the binding.

    :return: An existing SQLAlchemy session, or a newly created one.
    """
    session = getattr(g, SESSION_APP_CTX_KEY, None)
    if not session:
        _LOGGER.info("No session object cached. Creating a new one")
        # pylint: disable=protected-access
        db_state = current_app.extensions[DATABASE_EXTENSION_KEY]
        session = db_state._session_maker()
        setattr(g, SESSION_APP_CTX_KEY, session)
    else:
        _LOGGER.info("Using existing cached session object.")

    return session


# pylint: disable=too-many-arguments
def _make_sqlalchemy_url(
    *,
    engine: str,
    user: str,
    passwd: str,
    host: str,
    port: int,
    database: str,
    driver: str = "psycopg2",
) -> str:
    """Return a sqlAlchemy DB url."""
    if engine == "sqlite":
        return f"{engine}://"
    if engine == "postgresql":
        return f"{engine}+{driver}://{user}:{passwd}@{host}:{port}/{database}"
    raise ValueError(f"Unknown engine: {engine}")
