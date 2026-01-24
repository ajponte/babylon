"""Application-level configs."""

from typing import Any

from server.config.confload import (
    Loader,
    required,
    required_secret,
    optional,
    to_int,
    to_bool,
)

CONFIG_LOADERS: list[Loader] = [
    # These are optional for now. Later decide which should be required.
    required(key="BAO_ADDR"),
    required(key="OPENBAO_SECRETS_PATH"),
    # required(key="SQLALCHEMY_DATABASE_URL"),
    required(key="SQLALCHEMY_DB_ENGINE"),
    required(key="SQLALCHEMY_DATABASE_NAME"),
    optional(key="LOG_TYPE", default_val="stdout"),
    optional(key="LOG_LEVEL", default_val="DEBUG"),
    optional(key="SQLALCHEMY_POOL_RECYCLE", default_val="3600", converter=to_int),
    optional(key="SQLALCHEMY_INIT_TABLES", default_val="false", converter=to_bool),
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
