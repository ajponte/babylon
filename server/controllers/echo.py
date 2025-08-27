"""Connexion controller handlers."""
from http import HTTPStatus

import logging

_LOGGER = logging.getLogger()

def do_echo(value: str | None) -> tuple:
    """Echo a value."""
    _LOGGER.info(f'Echoing value {value}')
    return {'value': value}, HTTPStatus.OK
