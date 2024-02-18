# pylint: disable=W1203,fixme, unused-variable, no-member, line-too-long, too-many-arguments, unused-import, too-many-locals, broad-except, import-outside-toplevel
"""App Factory"""
from distutils.util import strtobool
from typing import Any, Dict, Callable, List, Union

from flask import Flask, Blueprint

from py_flaskbase.utils.healthcheck import make_healthcheck
from py_flaskbase.utils.metric.metrics import make_metrics_module
from py_flaskbase.utils.application.standalone import HeathCheckFilter
from py_flaskbase.utils.application.swagger import register_swagger_blueprint

# Register before and after actions
from py_flaskbase.utils.actions.before_actions import get_x_fwd, add_rid, add_start_time
from py_flaskbase.utils.actions.after_actions import add_response_time, add_rid_to_header
from py_flaskbase import cache
from py_flaskbase._version import __version__


def create(
    prefix: str = "/app",
    blueprints: Union[List[Blueprint], None] = None,
    run_before: Union[Dict[str, List[Callable[..., Any]]], None] = None,
    run_after: Union[Dict[str, List[Callable[..., Any]]], None] = None,
    healthchecks: Union[List[Callable[..., Any]], None] = None,
    config_obj: Union[str, None] = None,
    version_swagger_label: Union[str, None] = None,
) -> Flask:
    """
    Initialize the core application.

    :param prefix: The URI prefix that will be appened to all routes.
        This is required if running on Kubernetes  to ensure the application
        is routed correctly, defaults to "/app"
    :type prefix: str, optional
    :param blueprints: Define the blueprints you want the
        application to use, defaults to `None`
    :type blueprints: List[Blueprint], optional
    :param run_before: A dictionary with lists of
        functions that will be called at the beginning of each request.
        The key of the dictionary is the name of the blueprint this function is active for., defaults to `None`
    :type run_before: Dict[str, List[Callable]], optional
    :param run_after: A dictionary with lists of functions that should
        be called after each request. The key of the dictionary is the name of
        the blueprint this function is active for, defaults to `None`
    :type run_after: Dict[str, List[Callable]], optional
    :param healthchecks: List of funtions to be run when the healthcheck page is requested., defaults to `None`
    :type healthchecks: List[Callable], optional
    :param config_obj: Extra configuation for the application., defaults to None
    :type config_obj: str, optional
    :param version_swagger_label: Version of app to display on swagger docs, defaults to None
    :type version_swagger_label: str, optional
    :raises ValueError: _description_
    :raises TypeError: _description_
    :return: A Flask application.
    :rtype: Flask
    """
    if not prefix:
        raise ValueError("CONTEXT_ROOT can not be None")
    before = {None: [get_x_fwd, add_rid, add_start_time]}
    after = {None: [add_response_time, add_rid_to_header]}
    app = Flask(__name__, static_folder=None)
    app.logger.info(f"CONTEXT_ROOT={prefix},metrics-tool={__version__}")
    app.url_map.strict_slashes = False
    if config_obj:
        app.config.from_object(config_obj)
    app.logger.debug(f'msg="app configurations",config={app.config}')
    # Configure App Cache
    # https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching
    if "CACHE_TYPE" not in app.config:
        app.config["CACHE_TYPE"] = "flask_caching.backends.SimpleCache"
    if "CERT" not in app.config:
        app.config["CERT"] = False
    if "DEBUG" not in app.config:
        app.config["DEBUG"] = True
    elif not isinstance(app.config["DEBUG"], bool):
        try:
            app.config["DEBUG"] = strtobool(app.config["DEBUG"])
        except ValueError:
            app.logger.warning(f'DEBUG value must be boolean, got "{app.config["DEBUG"]}". Default to False')
            app.config["DEBUG"] = False
    cache.init_app(app, app.config)
    app.logger.debug('msg="initializing application plugins"')
    # Initialize Plugins
    with app.app_context():
        # Register Blueprints
        try:
            healthcheck: Blueprint = make_healthcheck(prefix=prefix, funcs=healthchecks)
            app.register_blueprint(healthcheck)
            app.register_blueprint(make_metrics_module(prefix=prefix))

            if not isinstance(blueprints, list):  # type: ignore
                raise TypeError(f"bluprints must be a callable list blueprints is {str(type(blueprints))}")
            for blueprint in blueprints:
                if not blueprint.url_prefix.startswith(f"{prefix}/"):
                    blueprint.url_prefix = f"{prefix}{blueprint.url_prefix}"
                app.logger.info(f'msg="blueprint_url created",{blueprint.name}={blueprint.url_prefix}')
                app.register_blueprint(blueprint)

            register_swagger_blueprint(app, prefix, version_swagger_label)

        except Exception as error:  # pragma: no cover
            app.logger.error(f"healthcheck_error={error}")

        if "AUTH_ENABLED" in app.config and str(app.config["AUTH_ENABLED"]).lower() == "true":
            from py_flaskbase.utils.actions import auth_request

            auth_request.validate_app_config()
            before[None].append(auth_request.auth_request)

        # TODO: check for none key
        try:
            if run_before:
                before.update(run_before)
            app.before_request_funcs = before
        except Exception as error:
            app.logger.error(f"run_before error={error}")

        try:
            if run_after:
                after.update(run_after)
            app.after_request_funcs = after
        except Exception as error:
            app.logger.error(f"run_after error={error}")

        # Register error handler
        from py_flaskbase.utils.error_handler import handle_exception
        from py_flaskbase.utils.error_handler import handle_http_exception
        from werkzeug.exceptions import HTTPException

        if not app.config["DEBUG"]:
            app.register_error_handler(Exception, handle_exception)
            app.logger.addFilter(HeathCheckFilter())
        else:
            app.logger.info("DEBUG logging enabled. Logging all tracebacks to log/console")
        app.register_error_handler(HTTPException, handle_http_exception)

    return app


def start(
    app: Flask,
    env: str = "dev",
    bind_address: str = "0.0.0.0",
    port: str = "8080",
    timeout: int = 15,
    number_of_workers: int = 3,
    number_of_threads: int = 1,
    log_format: Union[str, None] = None,
):
    """
    Start up Flask App.

    :param app: The app.
    :type app: Flask
    :param env: The environment the app is being run in.
        When set to dev the the app will run with the flask running,
        otherwise gunicorn will be used, defaults to `dev`
    :type env: str, optional
    :param bind_address: The IP to bind the applicaiton to, defaults to `'0.0.0.0'`
    :type bind_address: str, optional
    :param port: Port to listen, defaults to `'8080'`
    :type port: str, optional
    :param timeout: Timeout after this many seconds, defaults to `15`
    :type timeout: int, optional
    :param number_of_workers: How many workers to start and that will process pages.
        better to scale the number of nodes than add more workers, defaults to `3`
    :type number_of_workers: int, optional
    :param number_of_threads: How many threads per worker
        better to scale the number of nodes than add more workers, defaults to `1`
    :type number_of_threads: int, optional
    :param log_format: Log format, defaults to None
    :type log_format: str, optional
    """
    if env.lower() in ["development", "dev"]:
        app.logger.info("RUNNING DEV SERVER")
        app.run(
            host=bind_address,
            port=int(port),
            use_reloader=True,
            debug=True,
        )
    else:
        from py_flaskbase.utils.application.standalone import StandaloneApplication, CustomGunicornLogger
        from py_flaskbase.utils.application.gunicorn_conf import child_exit, on_starting, worker_exit, when_ready

        if not log_format:
            log_format = """%(t)s,remote_address="%(h)s",user=%(u)s,method="%(m)s",uri="%(U)s",query_string="%(q)s",request_time_in_ms=%(D)s,status_code=%(s)s,length=%(b)s,referer="%(f)s",agent="%(a)s",x-forwarded="%({x-forwarded-for}i)s" """

        app.logger.info(f"bind_address={bind_address},port={port},number_of_workers={number_of_workers},number_of_threads={number_of_threads}")

        options: dict[str, Any] = {
            "bind": f"{bind_address}:{port}",
            "workers": number_of_workers,
            "threads": number_of_threads,
            "timeout": timeout,
            "accesslog": "-",
            "access_log_format": log_format,
            "logger_class": "metrics_tool.application.standalone.CustomGunicornLogger",
            "child_exit": child_exit,
            "on_starting": on_starting,
            "worker_exit": worker_exit,
            "post_fork": when_ready,
        }
        StandaloneApplication(app, options).run()
