"""Event Wrapper."""

import json
from functools import wraps
from flask import g, request
from flask import current_app as app
from werkzeug.wrappers.response import Response


def _log_event(level: str, orch_id: str, action: str, message: dict, success: bool):
    level = level.upper()

    log = f'orch_id="{orch_id}" action="{action}" message={json.dumps(message)}'
    if success is not None:
        log += f" success={str(success)}"

    if level == "ERROR":
        app.logger.error(log)
    else:
        app.logger.info(log)


def extract_meaning(result: Response):
    """
    Use the message body and return error or message. Must have proper status_code defined.
    """
    message = {"result": {"status_code": result.status_code, "content_length": result.content_length}}
    level = "ERROR"
    if 199 <= result.status_code <= 299:
        level = "INFO"
    # if a dict, try to extract a message
    body = extract_response_json(result)
    if body:
        if "error" in body:
            message["error"] = body["error"]
        elif "message" in body:
            message["info"] = body["message"]
    return message, level


def extract_response_json(result):
    """
    Flask does not care if a payload is returned as a dict or a string, it
    serializes whatever you give it. This means it's possible to not have
    any messaging at all. If the data is not json, return None

    Eventually this method can/should be expanded to the Python 3.10 switch so
    we can handle any content type that a user would care to return... The
    authors prefer JSON over other content types for metrics purposes.
    """
    response_data = result.get_data()
    if not result.content_length:
        return None

    if result.content_type == "application/json":
        try:
            return json.loads(response_data)
        except json.JSONDecodeError:
            return None
    return None


def event(event_name=""):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            This wrapper is meant to decorate a flask route (inside the route
            decorator). It is responsible for identifying the orchestration id,
            logging the initiation of the REST call, and planting error or
            message information in the resultant object body. The "result" of
            a function call is any object that inherits from
            werkzeug.wrappers.response.Response

            """
            orch_id = g.rid

            if "orch_id" in request.headers:
                orch_id = request.headers["orch_id"]

            # log start of event
            _log_event("INFO", orch_id, event_name, {"info": f"Starting {event_name}"}, None)

            success = False
            try:
                result = func(*args, **kwargs)
                message, level = extract_meaning(result)
                if level == "INFO":
                    success = True
                _log_event(level, orch_id, event_name, message, success)
            except Exception as exception:
                level = "ERROR"
                message = {"error": str(exception), "result": None}
                # log exception
                _log_event(level, orch_id, event_name, message, success)
                raise exception
            return result

        return wrapper

    return actual_decorator
