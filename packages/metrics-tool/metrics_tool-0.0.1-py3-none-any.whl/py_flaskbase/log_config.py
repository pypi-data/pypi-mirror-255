"""Dict Config for Logging."""

import logging
from logging.config import dictConfig

from flask import has_app_context
from flask import current_app as app

from py_flaskbase.log_formatter import RequestFormatter


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "()": RequestFormatter,
                "format": "[%(asctime)s] level=%(levelname)s fn=%(filename)s ln=%(lineno)d func=%(funcName)s: %(message)s,%(context)s",
            }
        },
        "handlers": {"container": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout", "formatter": "default"}},
        "root": {"level": "INFO", "handlers": ["container"]},
    }
)

LOG = logging.getLogger(__name__)


def logger():
    if has_app_context():
        return app.logger
    else:
        return LOG
