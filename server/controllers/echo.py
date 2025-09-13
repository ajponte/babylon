"""Connexion controller handlers."""

from http import HTTPStatus

import logging

_LOGGER = logging.getLogger()


async def do_echo(input_val: str | None) -> tuple:
    """Echo a value."""
    _LOGGER.info(f"Echoing value {input_val}")
    return {"value": input_val}, HTTPStatus.OK
