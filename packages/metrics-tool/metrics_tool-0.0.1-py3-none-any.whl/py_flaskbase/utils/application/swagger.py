# pylint: disable=unused-variable, line-too-long
"""Configures swagger."""
import os

from flask_swagger_ui import get_swaggerui_blueprint
from flask_swagger import swagger
from flask import jsonify, Flask


def register_swagger_blueprint(app: Flask, prefix: str, version_swagger_label: str):
    """
    registers swagger UI blueprint to the application
    """
    swagger_json_url = "/json"
    app_name = prefix.replace("/", "")
    swagger_url = f"{prefix}/swagger"
    api_url = f"{swagger_url}{swagger_json_url}"
    swaggerui_blueprint = get_swaggerui_blueprint(swagger_url, api_url, config={"app_name": app_name, "validatorUrl": None})

    @swaggerui_blueprint.route(swagger_json_url)
    def get_swagger_api_json():
        """
        This api call generates a json file based on yaml annotations
        for the applications api calls in order to populate the
        swagger UI
        """
        try:
            original_dir = os.getcwd()
            os.chdir(app.config["ABSOLUTE_MODULE_PATH"])
            swag_json = swagger(app, from_file_keyword="swagger_from_file")
            os.chdir(original_dir)
        except Exception:
            raise LookupError("Invalid swagger doc string(s) provided. Unable to generate swagger json file")
        swag_json["info"]["version"] = version_swagger_label
        swag_json["info"]["title"] = f"{app_name.upper()} API"

        # Configure basic auth for swagger ui if AUTH_ENABLED is True
        if "AUTH_ENABLED" in app.config and str(app.config["AUTH_ENABLED"]).lower() == "true":
            swag_json["securityDefinitions"] = {"BasicAuth": {"type": "basic"}}

        for path in swag_json["paths"]:
            for rule in app.url_map._rules:
                for method in rule.methods:
                    method = method.lower()
                    rule_path = rule.rule.replace("<", "{").replace(">", "}")
                    if rule_path == path and method in swag_json["paths"][path]:
                        blueprint = rule.endpoint.split(".")[0]

                        # Tag each request with the name of it's corresponding blueprint
                        if "tags" in swag_json["paths"][path][method]:
                            swag_json["paths"][path][method]["tags"].append(blueprint)
                        else:
                            swag_json["paths"][path][method]["tags"] = [blueprint]

                        # Declare swagger request utilizes Basic-Auth authentication schema if AUTH_ENABLED
                        if "AUTH_ENABLED" in app.config and str(app.config["AUTH_ENABLED"]).lower() == "true":
                            swag_json["paths"][path][method]["security"] = [{"BasicAuth": []}]

        return jsonify(swag_json)

    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
