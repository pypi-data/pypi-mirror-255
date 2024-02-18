"""Init."""

from flask_caching import Cache

# TODO: Add rotate or daily logger and add additional
#   config parameters to globally set logging based on Config
from py_flaskbase.log_config import LOG, logger
from py_flaskbase._version import __version__

cache = Cache()
