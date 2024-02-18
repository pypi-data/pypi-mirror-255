# pylint: disable=too-few-public-methods, useless-object-inheritance
"""Application Config."""

import os
import pathlib
from typing import Any, Union
from flask import has_app_context
from flask import current_app as app


def enable_prometheus():
    """
    Prometheus enabled by default.
    """
    deprecated_env_var = os.environ.get("prometheus_multiproc_dir")
    current_env_var = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
    if deprecated_env_var and not current_env_var:
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = deprecated_env_var
    elif not deprecated_env_var and not current_env_var:
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = "/tmp"


class Config(object):
    """App configuration."""

    ABSOLUTE_MODULE_PATH = str(pathlib.Path(__file__).parent.parent.absolute())
    TEST_VAR = os.environ.get("TEST_KEY", None)
    AUTH_ENABLED = False
    AD_GROUPS = os.environ.get("AD_GROUPS", "Users")
    LDAP_URL = os.environ.get("LDAP_URL", "ldap://ldap.acme.com")
    AD_BASE_SEARCH = os.environ.get("ACTIVE_DIRECTORY_BASE_SEARCH", "dc=com")
    CERT = False
    MY_EMAIL_SERVER = os.environ.get("MY_EMAIL_SERVER", "acme.com")
    enable_prometheus()


def get_config(key: str, default: Any = None) -> Union[Any, None]:
    """Get Config Value."""
    if has_app_context():
        return app.config.get(key, default)
    return os.environ.get(key, default)
