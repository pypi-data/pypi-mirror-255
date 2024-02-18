# pylint: disable=W0223, line-too-long
"""Start a Flask application using gunicorn."""

import multiprocessing
import logging

from gunicorn import glogging
import gunicorn.app.base
from six import iteritems

multiprocessing.set_start_method("spawn", True)


class HeathCheckFilter(logging.Filter):
    """[summary]
    ignore logs from the kube-probe (health check and datadog agent) as they do
    not provide useful information
    Args:
        logging ([type]): [description]
    """

    FILTERS = ["kube-probe", "(health check)", "Datadog Agent/"]

    def filter(self, record):
        return not any(x in record.getMessage() for x in self.FILTERS)


class CustomGunicornLogger(glogging.Logger):
    """[summary]

    Args:
        glogging ([type]): [description]
    """

    def setup(self, cfg):
        """[summary]

        Args:
            cfg ([type]): [description]
        """
        super().setup(cfg)
        logger = logging.getLogger("gunicorn.access")
        logger.addFilter(HeathCheckFilter())


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """[summary]

    Arguments:
        gunicorn {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        """[summary]"""
        config = dict([(key, value) for key, value in iteritems(self.options) if key in self.cfg.settings and value is not None])

        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self.application
