# pylint: disable=C0301,R0913
"""Request wrapper for calls."""

import time
from typing import Dict, Union, Optional, Any

import requests
from requests.auth import AuthBase
from flask import Response

from py_flaskbase.log_config import logger
from py_flaskbase.config import get_config


def metrics_request(
    url: Optional[str] = None,
    method: Optional[str] = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth: Optional[AuthBase] = None,
    cert: Optional[Union[str, bool]] = None,
    retries: int = 2,
    timeout: int = 90,
) -> requests.Response:
    """
    Make an HTTP/HTTPS call.

    :param url: URL to send, defaults to None
    :type url: str, optional
    :param method: HTTP method to use, defaults to "GET"
    :type method: Optional[str], optional
    :param params: dictionary of URL parameters to append to the URL , defaults to None
    :type params: Optional[Dict], optional
    :param data: the body to attach the request. If a dictionary is provided, form-encoding will
        take place, defaults to None
    :type data: Union[str, Dict], optional
    :param headers: dictionary of headers to send, defaults to None
    :type headers: Optional[Dict[str, str]], optional
    :param auth: requests AuthBase object, defaults to None (ex: HTTPBasicAuth, HttpNtlmAuth, etc.)
    :type auth: AuthBase, optional
    :param cert: Cert for https calls, defaults to get_cert("CERT")
    :type cert: Union[str, bool], optional
    :param retries: number of times to retry a given request, defaults to 2
    :type retries: int, optional
    :param timeout: number of seconds request is allowed to take before timing out, defaults to 90
    :type timeout: int, optional
    :raises Exception: _description_
    :return: Response
    :rtype: requests.Response
    """

    if cert is None:
        cert = get_config("CERT") if get_config.get("CERT") else True

    # don't allow negative retries
    retries = max(retries, 0)

    url_no_args: str = url.split("?")[0]
    logger().info(f"request_action=metrics_call, url={url_no_args}")

    def _make_call() -> Response:
        start_time: float = time.time()

        try:
            with requests.Session() as session:
                req = requests.Request(method, params=params, url=url, data=data, headers=headers, auth=auth)
                prepped_req = session.prepare_request(req)
                _res = session.send(prepped_req, verify=cert, timeout=timeout)

            logger().info(
                ",".join(
                    [
                        f"request_action=metrics_call,url={url_no_args} method={method}",
                        f"status_code={_res.status_code}" f"dur_sec={_res.elapsed.total_seconds():.4f}",
                    ]
                )
            )
        except Exception as error:
            error_message: str = ",".join(
                [
                    f"request_action=metrics_call,url={url_no_args}",
                    f"method={method},dur_sec={time.time() - start_time}",
                    f'error="{error.__class__.__name__}: {str(error)}"',
                ]
            )
            logger().error(error_message)
            raise Exception(error_message)

        return _res

    for _ in range(retries):
        result: Response = _make_call()
        if result.status_code < 400:
            break
    else:
        logger().warning(f'request_action=metrics_call,url={url_no_args},method={method},error="max retries ({retries}) reached"')
    return result
