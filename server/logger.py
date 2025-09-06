# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
"""Logging wrapper."""
from logging.config import dictConfig

# Inspired by: https://github.com/tenable/flask-logging-demo/blob/master/single_file_app_pattern/flask_logs.py
# See https://medium.com/tenable-techblog/the-boring-stuff-flask-logging-21c3a5dd0392

# We have options in python for stdout (streamhandling) and file logging
# has options for a Rotating file based on size or time (daily)
# or a watched file, which supports logrotate style rotation
# Most of the changes happen in the handlers, lets define a few standards


STDOUT_DEFAULTS = {
    "LOG_TYPE": "stream",
    "LOG_LEVEL": "DEBUG",
    "LOG_DIR": "",
    "APP_LOG_NAME": "default",
    "WWW_LOG_NAME": "",
}


def get_defaults() -> dict[str, str]:
    """Return default logging policy."""
    return STDOUT_DEFAULTS


class LogSetup:
    """Logging object."""

    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        # pylint: disable=too-many-locals
        """
        Initialize logging for a flask app.

        :param app: The flask app.
        """
        initialize_defaults: bool = kwargs.get("default_policy", False)
        app_config: dict = app.config if not initialize_defaults else STDOUT_DEFAULTS
        log_type = app_config.get("LOG_TYPE", None) or kwargs.get("log_type")
        logging_level = app_config.get("LOG_LEVEL", None) or kwargs.get("log_level")
        if log_type != "stream":
            try:
                log_directory = app_config["LOG_DIR"]
                app_log_file_name = app_config["APP_LOG_NAME"]
                access_log_file_name = app_config["WWW_LOG_NAME"]
            except KeyError as e:
                # pylint: disable=consider-using-sys-exit
                exit(code=f"{e} is a required parameter for log_type '{log_type}'")
            app_log = "/".join([log_directory, app_log_file_name])
            www_log = "/".join([log_directory, access_log_file_name])

        if log_type == "stream":
            logging_policy = "logging.StreamHandler"
        elif log_type == "watched":
            logging_policy = "logging.handlers.WatchedFileHandler"
        else:
            log_max_bytes = app_config["LOG_MAX_BYTES"]
            log_copies = app_config["LOG_COPIES"]
            logging_policy = "logging.handlers.RotatingFileHandler"

        std_format = {
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(funcName)s: %(message)s",
                    "datefmt": "%d/%b/%Y:%H:%M:%S",
                },
                "access": {"format": "%(message)s"},
            }
        }
        std_logger = {
            "loggers": {
                "": {
                    "level": logging_level,
                    "handlers": ["default"],
                    "propagate": True,
                },
                "app.access": {
                    "level": logging_level,
                    "handlers": ["access_logs"],
                    "propagate": False,
                },
                "root": {"level": logging_level, "handlers": ["default"]},
            }
        }
        if log_type == "stream":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": logging_level,
                        "formatter": "default",
                        "class": logging_policy,
                    },
                    "access_logs": {
                        "level": logging_level,
                        "class": logging_policy,
                        "formatter": "access",
                    },
                }
            }
        elif log_type == "watched":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": logging_level,
                        "class": logging_policy,
                        # pylint: disable=possibly-used-before-assignment
                        "filename": app_log,
                        "formatter": "default",
                        "delay": True,
                    },
                    "access_logs": {
                        "level": logging_level,
                        "class": logging_policy,
                        # pylint: disable=possibly-used-before-assignment
                        "filename": www_log,
                        "formatter": "access",
                        "delay": True,
                    },
                }
            }
        else:
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": logging_level,
                        "class": logging_policy,
                        "filename": app_log,
                        "backupCount": log_copies,
                        "maxBytes": log_max_bytes,
                        "formatter": "default",
                        "delay": True,
                    },
                    "access_logs": {
                        "level": logging_level,
                        "class": logging_policy,
                        "filename": www_log,
                        "backupCount": log_copies,
                        "maxBytes": log_max_bytes,
                        "formatter": "access",
                        "delay": True,
                    },
                }
            }

        log_config = {
            "version": 1,
            "formatters": std_format["formatters"],
            "loggers": std_logger["loggers"],
            "handlers": logging_handler["handlers"],
        }
        dictConfig(log_config)


# Initialize logging
logs = LogSetup()
