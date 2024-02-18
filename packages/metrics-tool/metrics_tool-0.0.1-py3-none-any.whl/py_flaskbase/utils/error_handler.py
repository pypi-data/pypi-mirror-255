"""Error Handlers."""

from typing import Union
import json

from flask import current_app as app
from flask import Response
from werkzeug.exceptions import HTTPException


def handle_http_exception(error: HTTPException) -> Response:
    """
    Turn HTTP errors into JSON.

    :param error: The thrown error
    :type error: HTTPException
    :return: JSON
    :rtype: Response
    """
    response: Response = error.get_response()
    response.data = json.dumps(
        {
            "code": error.code,
            "name": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response


def handle_exception(error: Exception) -> Response:
    """
    Handle an exception and return a JSON response.

    :param error: The thrown error
    :type error: HTTPException
    :return: JSON
    :rtype: Response
    """
    app.logger.error(error)
    data: dict[str, Union[int, str]] = {"code": 500, "name": "Internal Server Error", "description": str(error)}
    response = app.response_class(response=json.dumps(data), status=500, mimetype="application/json")
    return response
