"""After Request Processes/Actions."""

import time

from flask import g, Response, request
from flask import current_app as app


def add_rid_to_header(response: Response) -> Response:
    """
    Add the rid to the header.

    :param response: The response to the request
    :type response: Response
    :return: Modified Response.
    :rtype: Response
    """
    response.headers["rid"] = g.rid
    return response


def add_response_time(response: Response) -> Response:
    """
    Calualate the total processesing time for the request
    and log it out.

    :param response: The response to the request
    :type response: Response
    :return: The modifed response.
    :rtype: Response
    """
    if not any(
        key in request.path
        for key in [
            "healthcheck",
            "metrics",
        ]
    ):
        try:
            response_time = time.time() - g.request_start_time
            app.logger.info(f"response_time={round(response_time, 7)}")
        except Exception as error:
            app.logger.warn(error)
    return response
