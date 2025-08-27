"""App factory."""

import logging
from http import HTTPStatus
import sys

import datetime as dt
from typing import Any
from connexion import FlaskApp # type: ignore
from werkzeug.exceptions import NotFound

from flask import Flask, request, jsonify
from flask_cors import CORS

from server.config.config import (
    update_config_from_environment,
    update_config_from_secrets,
)
from server.db import Database
from server.logger import logs
from server.models import BASE
from server.health import health

# todo: Temporary fix
USE_DEFAULT_LOGGING_POLICY = True
DEFAULT_SWAGGER_API_SOURCE = "test-api.yml"


def create_app() -> Flask:
    """
    Create a new Flask app.

    :return: The new Flask app.
    """
    app = FlaskApp(__name__)
    try:
        app.add_api(
            specification=DEFAULT_SWAGGER_API_SOURCE,
            pythonic_params=True,
            validate_responses=True,
            strict_validation=True,
        )
    except Exception as e:
        logging.error("Failed to load OpenAPI spec: %s", e)
        sys.exit(1)  # Exit the application gracefully
    flask_app = app.app
    _setup_logging(flask_app)
    _setup_config(flask_app)
    _register_app_extensions(flask_app)
    # Enable Cross-Origin Resource Sharing (currently for dev).
    CORS(flask_app)
    _setup_health_route(flask_app)
    _setup_http_error_handling(flask_app)
    return flask_app


def _setup_http_error_handling(flask_app):
    _handle_error_unknown(flask_app)
    # Add a catch-all handler for any exception that isn't handled by a more specific handler.
    _handle_base_exception(flask_app)
    _handle_not_found(flask_app)


def _handle_error_unknown(flask_app: Flask):
    """
    Hande a response from the server when an unknown error is encountered.
    """

    @flask_app.errorhandler(500)
    def error(e: Any | None):
        resp = {
            "message": f"Unknown server error: {str(e)}",
            "status": HTTPStatus.INTERNAL_SERVER_ERROR,
        }
        return jsonify(resp)

    # flask_app.register_error_handler(error)


def _handle_base_exception(flask_app: Flask):
    """
    Handle any base exception and return a generic 500 error response.
    """

    @flask_app.errorhandler(Exception)
    def handle_base_exception(e):
        resp = {
            "message": f"A base exception was caught: {str(e)}",
            "status": HTTPStatus.INTERNAL_SERVER_ERROR,
        }
        return jsonify(resp), 500


def _handle_not_found(flask_app: Flask):
    """
    Handle 404 Not Found errors.
    """

    @flask_app.errorhandler(NotFound)
    def handle_not_found_error(e):
        resp = {"message": f"Not Found: {str(e)}", "status": HTTPStatus.NOT_FOUND}
        return jsonify(resp), 404


def _setup_logging(
    flask_app: Flask,
):
    """
    Setup logging.
    """
    # Init logs
    logs.init_app(flask_app, default_policy=USE_DEFAULT_LOGGING_POLICY)

    # For request logging
    @flask_app.after_request
    def after_request(response):
        """
        Application logging.

        :param response: Application response.
        :return: response
        """
        logger = logging.getLogger("app.access")
        logger.info(
            "%s [%s] %s %s %s %s %s %s %s",
            request.remote_addr,
            dt.datetime.now().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
            request.method,
            request.path,
            request.scheme,
            response.status,
            response.content_length,
            request.referrer,
            request.user_agent,
        )
        return response


def _setup_config(flask_app: Flask):
    """
    Set up the flask app config.

    :param flask_app: The flask app.
    """
    config: dict[str, Any] = {}
    update_config_from_environment(config)
    update_config_from_secrets(config)
    flask_app.config.from_mapping(config)


def _register_app_extensions(
    flask_app: Flask,
):
    """
    Register flask app extensions.

    :param flask_app: The app.
    """
    # # Init logs
    # logs.init_app(flask_app, default_policy=USE_DEFAULT_LOGGING_POLICY)
    with flask_app.app_context():
        flask_app.Database = Database(flask_app.config, BASE)  # type: ignore
        flask_app.Database.attach_to_flask_app(  # type: ignore
            flask_app=flask_app,
            create_tables=flask_app.config.get("SQLALCHEMY_INIT_TABLES", False),
        )


def _setup_health_route(flask_app: Flask):
    """
    Set up a /health route.

    :param flask_app: The app.
    """
    flask_app.add_url_rule("/health", view_func=health)
