# pylint: disable=no-name-in-module
"""Prometheus Metrics."""

from typing import Any

import sys
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from prometheus_client.utils import INF

from flask import Blueprint, Response, current_app as app

from py_flaskbase.config import Config as config


ERR = Counter(
    "exceptions",
    "Count of Exceptions",
    labelnames=["func"],
)


T = Gauge("run_time", "Runtime Seconds", labelnames=["func"], unit="secs")

GENERIC_HISTOGRAM = Histogram("processing_time", "Processing Seconds Histogram", labelnames=["func"], unit="secs")

SDK_CALL_HISTOGRAM = Histogram(
    "sdk_call_time",
    "Processing Seconds Histogram for SDK function calls involving calls to remote data sources",
    labelnames=["func"],
    unit="secs",
    buckets=(0.5, 1, 2.5, 5.0, 10.0, 15, 20, 30, 40, 50, 60, 70, 80, 90, INF),
)

LONG_SDK_CALL_HISTOGRAM = Histogram(
    "long_sdk_call_time",
    "Processing Seconds Histogram for SDK function calls involving very long calls to remote data sources",
    labelnames=["func"],
    unit="secs",
    buckets=(5, 10, 20, 30, 45, 60, 90, 120, 150, 180, 210, 240, 270, 300, INF),
)


def get_metrics(event_name=""):
    """
    Get Metric Event Decorator.

    :param event_name: _description_, defaults to ""
    :type event_name: str, optional
    """

    def actual_decorator(func):
        """[summary]

        Args:
            func ([type]): [description]

        Returns:
            [type]: [description]
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            """[summary]

            Returns:
                [type]: [description]
            """
            lbl: str = f"{sys.modules[func.__module__].__name__}.{func.__name__}"
            hist: Histogram = GENERIC_HISTOGRAM.labels(lbl)
            err: Counter = ERR.labels(lbl)
            timeit: Gauge = T.labels(lbl)

            with hist.time(), err.count_exceptions(), timeit.time():
                result: Any = func(*args, **kwargs)

            return result

        return wrapper

    return actual_decorator


def process_metrics(event_name: str = ""):
    """
    process-specific metrics call, identical to original single "metrics"
    decorator, but with "process_" in the name so developers know what you
    intend to time

    Args:
        event_name (str, optional): [description]. Defaults to "".
    """

    def process_metrics_decorator(func):
        """[summary]

        Args:
            func ([type]): [description]

        Returns:
            [type]: [description]
        """

        @wraps(func)
        def wrapper(*args: list[Any], **kwargs: Any) -> Any:
            """[summary]

            Returns:
                [type]: [description]
            """
            lbl: str = f"{sys.modules[func.__module__].__name__}.{func.__name__}"
            hist: Histogram = GENERIC_HISTOGRAM.labels(lbl)
            err: Counter = ERR.labels(lbl)
            timeit: Gauge = T.labels(lbl)

            with hist.time(), err.count_exceptions(), timeit.time():
                result: Any = func(*args, **kwargs)

            return result

        return wrapper

    return process_metrics_decorator


def sdk_call_metrics():
    """
    Use this decorator when your function is about to make an external call
    that does not (or cannot) utilize metrics_request. Usually when using a 3rd
    party SDK. This metric will always capture processing time as well as
    request response time. This is not an accurate measure of the external call
    time! For that you need a profile.

    With

    Args:
        event_name (str, optional): [description]. Defaults to "".
    """

    def sdk_call_metrics_decorator(func):
        """[summary]

        Args:
            func ([type]): [description]

        Returns:
            [type]: [description]
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """[summary]

            Returns:
                [type]: [description]
            """
            lbl = f"{sys.modules[func.__module__].__name__}.{func.__name__}"
            hist = SDK_CALL_HISTOGRAM.labels(lbl)
            err = ERR.labels(lbl)
            timeit = T.labels(lbl)

            with hist.time(), err.count_exceptions(), timeit.time():
                result = func(*args, **kwargs)

            return result

        return wrapper

    return sdk_call_metrics_decorator


def long_sdk_call_metrics():
    """
    Identical to sdk_call_metrics, but utilizes buckets of up to 300 sec. For
    most requests this is an absurdly long timeout, and so this decorator is
    here for long term modeling of poorly running SDKs/endpoints. IE gathering
    data necessary to find better solutions. IF you find yourself relying on
    this metric long-term, you should seriously consider message queueing.

    Args:
        event_name (str, optional): [description]. Defaults to "".
    """

    def long_sdk_call_metrics_decorator(func):
        """[summary]

        Args:
            func ([type]): [description]

        Returns:
            [type]: [description]
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """[summary]

            Returns:
                [type]: [description]
            """
            lbl = f"{sys.modules[func.__module__].__name__}.{func.__name__}"
            hist = LONG_SDK_CALL_HISTOGRAM.labels(lbl)
            err = ERR.labels(lbl)
            timeit = T.labels(lbl)

            with hist.time(), err.count_exceptions(), timeit.time():
                result = func(*args, **kwargs)

            return result

        return wrapper

    return long_sdk_call_metrics_decorator


def make_metrics_module(prefix) -> Blueprint:
    app_metrics = Blueprint("metrics", __name__)

    @app_metrics.route("/metrics")
    @app_metrics.route(f"{prefix}/metrics")
    def get_app_metrics():
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    return app_metrics
