# pylint: disable=invalid-name, unused-variable
"""App Healthcheck."""

import sys
from typing import Any, Callable, List, Union

from flask import current_app as app
from flask import Blueprint, jsonify, g

from py_flaskbase.utils.metric.metrics import get_metrics
from py_flaskbase._version import __version__


def make_healthcheck(prefix: Union[str, None] = None, funcs: Union[List[Callable[..., Any]], None] = None) -> Blueprint:
    """
    Perform basic health check.  The following data is returned:

        * after_funcs
        * before_funcs
        * rid
        * client_ip
        * routes
        * additional_health_checks

    :param prefix: Application URI prefix, defaults to None
    :type prefix: str, optional
    :param funcs: List of functions to call, defaults to None
    :type funcs: List[Callable], optional
    :return: JSON Object
    :rtype: Blueprint
    """
    prefix = prefix if prefix else ""

    healthcheck = Blueprint("healthcheck", __name__)

    @healthcheck.route("/healthcheck")
    @get_metrics(event_name="healthcheck")
    def do_healthcheck():  # type: ignore
        """
        Health Check
        ---
        responses:
          200:
            description: returns health of app and api map
        """
        app.logger.debug("action=healthcheck")

        routes = [{str(rule): list(rule.methods)} for rule in app.url_map.iter_rules()]

        after = {}
        before = {}
        for key in app.before_request_funcs:
            before[str(key)] = [f.__name__ for f in app.before_request_funcs[key]]

        for key in app.after_request_funcs:
            after[str(key)] = [f.__name__ for f in app.after_request_funcs[key]]

        hc = {
            "after_funcs": after,
            "before_funcs": before,
            "rid": g.rid,
            "client_ip": g.ip_addr,
            "routes": routes,
            "metrics_tool_version": __version__,
            "python_version": sys.version,
            "env": app.config.get("ENV", None),
        }

        if funcs:
            for func in funcs:
                try:
                    hc[func.__name__] = func()
                except Exception as error:
                    app.logger.error(error)

        return jsonify(hc)

    return healthcheck
