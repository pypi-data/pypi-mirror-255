"""Run Sample App."""

from flask import g, Blueprint, jsonify

from py_flaskbase import __version__
from py_flaskbase.utils.application import create, start
from py_flaskbase.utils.metric.metrics import get_metrics
from py_flaskbase.config import Config

BLUEPRINT_V1 = "/api/v1"
TEST = Blueprint("test", __name__, url_prefix=f"{BLUEPRINT_V1}/test")


def get_app():
    """Get app test."""


def health_check_true():
    """Set healthcheck test."""
    return True


def add_global():
    """Sample add global actions."""
    g.stuff = "stuff here"


@TEST.get("/")
@get_metrics(event_name="Metrics Test event")
def test_request():
    """
    Test request
    ---
    responses:
      200:
        description: returns a welcoming message
    """
    return jsonify({"message": "hello"})


APP = create(
    prefix="/test_app",
    blueprints=[TEST],
    run_before={"test": [add_global]},
    healthchecks=[health_check_true],
    config_obj=Config,
    version_swagger_label=__version__,
)

start(APP)
