"""Application-level configs."""

from typing import Any

from server.config.confload import Loader, required, required_secret, optional, to_int, to_bool


# XXX: Temporary. Should be removed in favor of just using env vars.
def make_sqlalchemy_url(
    engine: str = "sqlite",
    user: str = "user",
    passwd: str = "password",
    host: str = "localhost",
    port: int = 5432,
    database: str = "babylon"
) -> str:
    """Return a sqlaclchemy DB url."""
    if engine == "sqlite":
        return f"{engine}://"
    elif engine == 'postgresql':
        driver = "psycopg2"
        return f"{engine}+{driver}://{user}:{passwd}@{host}:{port}/{database}"
    raise ValueError(f"Unknown engine: {engine}")


CONFIG_LOADERS: list[Loader] = [
    # These are optional for now. Later decide which should be required.
    required(key="BAO_ADDR"),
    required(key="OPENBAO_SECRETS_PATH"),
    optional(key="LOG_TYPE", default_val="stdout"),
    optional(key="LOG_LEVEL", default_val="DEBUG"),
    optional(
        key="SQLALCHEMY_DATABASE_URL",
        default_val=make_sqlalchemy_url()
    ),
    optional(key="SQLALCHEMY_POOL_RECYCLE", default_val="3600", converter=to_int),
    optional(key='SQLALCHEMY_INIT_TABLES', default_val="false", converter=to_bool)
]

SECRETS_LOADERS: list[Loader] = [
    required_secret(key="DB_HOST", path="test"),
    required_secret(key="DB_PORT", path="test"),
    required_secret(key="DB_USERNAME", path="test"),
    required_secret(key="DB_PASSWORD", path="test"),
]


def update_config_from_environment(config: dict[str, Any]) -> None:
    """
    Return an updated config dict whose values are from the OS environment.

    :param config: The dict to update.
    """
    config.update(dict(loader() for loader in CONFIG_LOADERS))


def update_config_from_secrets(config: dict[str, Any]) -> None:
    """
    Update an existing config with values from the secrets store.

    :param config: The config dict to update.
    """
    config.update(dict(loader() for loader in SECRETS_LOADERS))
