"""App factory."""
import logging
import datetime as dt
from flask import Flask, request
from flask_cors import CORS

from server.config.config import update_config_from_environment, update_config_from_secrets
from server.db import Database
from server.logger import logs
from server.models import BASE
from server.health import health

def create_app() -> Flask:
    """
    Create a new Flask app.

    :return: The new Flask app.
    """
    app = Flask(__name__)
    _setup_config(app)
    _register_app_extensions(app)
    # Enable Cross-Origin Resource Sharing (currently for dev).
    CORS(app)
    _setup_health_route(app)

    return app

def _setup_config(flask_app: Flask):
    """
    Set up the flask app config.

    :param flask_app: The flask app.
    """
    config = {}
    update_config_from_environment(config)
    update_config_from_secrets(config)
    flask_app.config.from_mapping(config)

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

def _register_app_extensions(flask_app: Flask):
    """
    Register flask app extensions.

    :param flask_app: The app.
    """
    # Init logs
    logs.init_app(flask_app)
    with flask_app.app_context():
        flask_app.Database = Database(flask_app.config, BASE)
        flask_app.Database.attach_to_flask_app(
            flask_app=flask_app,
            create_tables=flask_app.config.get('SQLALCHEMY_INIT_TABLES', False)
        )

def _setup_health_route(flask_app: Flask):
    """
    Set up a /health route.

    :param flask_app: The app.
    """
    flask_app.add_url_rule('/health', view_func=health)
