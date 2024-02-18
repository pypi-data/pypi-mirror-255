"""Standard Log Formatter Template."""

import re
from logging import Formatter
from flask import g, request, has_request_context


class RequestFormatter(Formatter):
    """
    Request Formatter.

    :param Formatter: _description_
    :type Formatter: _type_
    """

    def format(self, record):
        record.context = ""
        if has_request_context():
            if g.get("rid") and g.get("ip_addr"):
                record.context = "rid={},path='{}',ip='{}'".format(g.rid, request.full_path, g.ip_addr)
            else:
                record.context = "path='{}'".format(request.full_path)
        else:
            record.msg = re.sub(r"\[.*?\]", "", record.msg, flags=re.DOTALL)
            if g and g.get("rid"):
                record.msg = "{},rid={}".format(record.msg, g.rid)

        return super().format(record)
