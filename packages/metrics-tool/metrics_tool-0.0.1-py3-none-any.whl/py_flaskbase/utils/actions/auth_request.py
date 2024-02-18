# pylint: disable=no-member,W0703,C0103,raise-missing-from
"""Configure authorization agains AD"""

import base64
import json
from typing import Any, Union
import ldap

from flask import request
from flask import current_app as app

from py_flaskbase import cache
from py_flaskbase.exceptions import LdapException


def ad_cache(*args, **kwargs):
    """
    AD Cache.

    :return: _description_
    :rtype: _type_
    """
    if "Authorization" in request.headers:
        return request.headers["Authorization"]
    else:
        return ""


def auth_request():
    """
    Authorize Requests.

    Using the basic auth value of the Authorization header, look up user
    in AD and validate they are a member of the group defined in
    app.config["AD_GROUP"]. If user is unauthorized 401 response will be returned
    """

    # do not check auth for healthcheck or swagger_ui blueprints
    # Note: calls made via the swagger UI will still require basic auth
    if request.blueprint in ["healthcheck", "swagger_ui", "metrics"]:
        if "kube-probe" not in request.headers.get("User-Agent"):
            app.logger.info(f"skipping authorization check for {request.blueprint}")
        return
    app.logger.info("Checking Auth")
    try:
        AD_USER, AD_PW = base64.b64decode(request.headers["Authorization"].replace("Basic ", "")).decode().split(":")

        auth = validate_user(user_name=AD_USER, password=AD_PW)
        if auth[0] is False:
            data = {"error": f"Not Authorized: {auth[1]}"}
            app.logger.warning(f"Not Authorized: {auth[1]}")
            response = app.response_class(response=json.dumps(data), status=401, mimetype="application/json")
            return response

    except KeyError as error:
        app.logger.warning(f"KeyError {error}")
        data = {"error": f"Issue with authorization {str(error)}"}
        response = app.response_class(response=json.dumps(data), status=401, mimetype="application/json")
        return response
    except Exception as error:
        app.logger.warning(f"auth_error={error} ")
        data = {"error": f"Issue with authorization {str(error)}"}
        response = app.response_class(response=json.dumps(data), status=401, mimetype="application/json")
        return response


def get_ad_info(ldap_user: str, ldap_pass: str, username: str, ldap_dc: str) -> Union[dict[str, Any], None]:
    """
    Get AD information from LDAP about a given user including
    memberOf and lockoutTime.

    :param ldap_user: user used to connect to ldap
    :type ldap_user: str
    :param ldap_pass: password of user used to connect to ldap
    :type ldap_pass: str
    :param username: username of AD object being queried
    :type username: str
    :param ldap_dc: dc for username. Example: acme.com
    :type ldap_dc: str
    :raises LdapException: Error Raised connecting to LDAP.
    :return: ad_info
    :rtype: Union[dict[str,Any], None]
    """
    try:
        connect = ldap.initialize(app.config["LDAP_URL"])
        connect.set_option(ldap.OPT_REFERRALS, 0)
        connect.simple_bind_s("{}@{}".format(ldap_user), ldap_pass)
        result = connect.search_s(app.config["AD_BASE_SEARCH"], ldap.SCOPE_SUBTREE, f"sAMAccountName={username}", ["memberOf", "lockoutTime"])
    except Exception as e:
        raise LdapException(f"Exception occured in get_ad_info: {e}")

    if result[0][0] is None:
        return None

    lockoutTime = 0
    if "lockoutTime" in result[0][1]:
        lockoutTime = result[0][1]["lockoutTime"]

    ad_info: dict[str, Any] = {"memberOf": result[0][1]["memberOf"], "lockoutTime": lockoutTime}

    return ad_info


@cache.cached(timeout=20 * 60, key_prefix=ad_cache)
def validate_user(user_name: str, password: str):
    """Valdate a user is in a specific group

    Caches for 1 hour

    Arguments:
        user_name {str} -- user to query
        password {str} -- password of user

    Returns:
        [boolean, str] --  is valid, error message
    """

    is_valid = False

    msg = ""
    try:
        user_ad_info = get_ad_info(user_name, password, user_name)
        if user_ad_info is None:
            return False, f"AD info for user {user_name} was not found in the ldap"
    except Exception as e:
        msg = str(e)
        app.logger.error(msg)
        return is_valid, msg

    allowed_groups = app.config["AD_GROUPS"]

    for user_group in user_ad_info["memberOf"]:
        if user_group.decode("utf-8") in allowed_groups:
            return True, "Validated"

    return False, f"User {user_name} is not a member of any of the allowed groups {allowed_groups}"


def validate_app_config():
    """Validate auth values for an application"""
    required_keys = ["AD_GROUPS", "LDAP_URL", "AD_BASE_SEARCH"]
    for key in required_keys:
        if key not in app.config:
            error = f"{key} not found in application config and is required when AUTH_ENABLED==true"
            app.logger.warning(error)
            raise KeyError(error)
