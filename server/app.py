"""App factory."""

import logging
from http import HTTPStatus
import sys

import datetime as dt
from pathlib import Path
from typing import Any
from connexion import FlaskApp  # type: ignore
from werkzeug.exceptions import NotFound

from flask import Flask, request, jsonify
from flask_cors import CORS

from server.config.config import (
    update_config_from_environment,
    update_config_from_secrets,
    load_hashicorp_secrets,
)

from server.db import Database
from server.logger import logs
from server.models import BASE
from server.health import health

# todo: Temporary fix
USE_DEFAULT_LOGGING_POLICY = True
DEFAULT_SWAGGER_API_SOURCE = "babylon-api-spec.yml"


def create_app() -> FlaskApp:
    """
    Create a new Flask app.

    :return: The new Flask app.
    """
    print("--- Entering create_app ---")
    spec_path = get_api_spec_path(DEFAULT_SWAGGER_API_SOURCE)
    print(f"full spec path: {spec_path}")
    app = FlaskApp(__name__)
    print("Connexion FlaskApp created.")
    try:
        app.add_api(
            specification=spec_path,
            pythonic_params=True,
            validate_responses=True,
            strict_validation=True,
        )
        print("Successfully added API spec")
        flask_app = app.app
        print("Flask app instance obtained.")

        print("--- Starting setup functions ---")
        print("Setting up logging...")
        _setup_logging(flask_app)
        print("Logging setup complete.")

        print("Setting up config...")
        _setup_config(flask_app)
        print("Config setup complete.")

        print("Registering app extensions...")
        _register_app_extensions(flask_app)
        print("App extensions registered.")

        print("Setting up CORS...")
        CORS(flask_app)
        print("CORS setup complete.")

        print("Setting up health route...")
        _setup_health_route(flask_app)
        print("Health route setup complete.")

        print("Setting up HTTP error handling...")
        _setup_http_error_handling(flask_app)
        print("HTTP error handling setup complete.")

        print("--- create_app finished successfully ---")
        return app
    except Exception as e:
        print(f"CRITICAL ERROR during application setup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1) # Ensure Gunicorn worker fails to boot with a logged error


# pylint: disable=unused-argument
def decode_token(token) -> dict:
    """
    Decode token method for bearer auth scheme.
    This is the function registered with the spec's `securitySchemes`.

    :param token: Bearer token.
    :return: Dict containing possible user info.
    """
    # todo
    return {}


def _setup_http_error_handling(flask_app):
    _handle_error_unknown(flask_app)
    # Add a catch-all handler for any exception that isn't handled by a more specific handler.
    _handle_base_exception(flask_app)
    _handle_error_not_found(flask_app)


# Handler for 500 errors (moved from _handle_error_unknown)
def handle_500_error(e: Any | None):
    resp = {
        "message": f"Unknown server error: {str(e)}",
        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
    }
    return jsonify(resp)

def _handle_error_not_found(flask_app: Flask):
    """Handles 404 errors."""
    flask_app.register_error_handler(500, handle_500_error)

def _handle_error_unknown(flask_app: Flask):
    """
    Handle a response from the server when an unknown error is encountered.
    """
    flask_app.register_error_handler(500, handle_500_error)


# Handler for generic exceptions (moved from _handle_base_exception)
def handle_generic_exception(e):
    resp = {
        "message": f"A base exception was caught: {str(e)}",
        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
    }
    return jsonify(resp), 500

def _handle_base_exception(flask_app: Flask):
    """
    Handle any base exception and return a generic 500 error response.
    """
    flask_app.register_error_handler(Exception, handle_generic_exception)


def _setup_logging(
    flask_app: Flask,
):
    """
    Setup logging.
    """
    # Init logs
    logs.init_app(flask_app, log_level="DEBUG", log_type="stream")

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
    load_hashicorp_secrets()
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


def get_api_spec_path(filename: str) -> Path:
    """
    Returns a pathlib.Path object for a given API spec filename.

    This function assumes the API specification files are located in the
    './api_spec/' directory relative to the current working directory.

    :param filename: The name of the API specification file (e.g., "test-api.yml").

    :return: Path: A Path object representing the full path to the API spec file.
    """
    # Get the base directory of the project (parent of the current file's directory)
    base_dir = Path(__file__).parent.parent

    # Construct the full path to the API spec file
    api_spec_path = base_dir / "api_spec" / filename

    # Return the Path object
    return api_spec_path
