"""Before Request Process/Actions."""

import uuid
import time

from flask import g, request
from flask import current_app as app


def add_start_time():
    """
    Add Start time to the request so a total response time can be generated
    """
    g.request_start_time = time.time()


def add_rid():
    """
    Add a request id (rid) to the request.  If the header has 'rid' that value will be use
    if not a UUID will be generated for this request.   The rid is is used to associate multiple
    method calls to a request.

    Calls to app.logger will automaticlly have the rid appened to the log entry.
    """
    if "rid" in request.headers:
        g.rid = request.headers["rid"]
    else:
        g.rid = uuid.uuid4().hex


def get_x_fwd():
    """
    Add the IP addreess or X-Forwarded-For for if present in the header.
    """
    if request.headers.getlist("X-Forwarded-For"):
        g.ip_addr = request.headers.getlist("X-Forwarded-For")[0]
    else:
        g.ip_addr = request.remote_addr
