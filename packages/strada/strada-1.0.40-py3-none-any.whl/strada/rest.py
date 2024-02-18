import json
import builtins

from .sdk import HttpRequestExecutor
from .exception_handler import exception_handler
from .common import (
    basic_auth_str,
    build_input_schema_from_strada_param_definitions,
        custom_print
)
from .debug_logger import with_debug_logs

# Initialize the print function to use the logger
builtins.print = custom_print


class CustomHttpActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "CustomHTTPAction"

    def set_param_schema(self, param_schema):
        self._get_instance().param_schema_definition = (
            build_input_schema_from_strada_param_definitions(param_schema)
        )
        return self

    def set_url(self, url):
        self._get_instance().url = url
        return self

    def set_method(self, method):
        self._get_instance().method = method
        return self

    def set_token(self, access_token):
        self._get_instance().token = access_token
        return self

    def set_api_key(self, api_key):
        self._get_instance().api_key = api_key
        return self

    def set_basic_auth(self, basic_auth):
        self._get_instance().basic_auth = basic_auth
        return self

    def set_headers(self, headers):
        self._instance.headers = headers
        return self

    def set_params(self, params):
        self._instance.params = params
        return self

    def set_body(self, body):
        self._instance.body = body
        return self
    
    def set_function_name(self, function_name):
        if function_name is None:
            self._instance.function_name = self.default_function_name
        else:
            self._instance.function_name = function_name
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = CustomHttpAction()
        return self._instance


class CustomHttpAction:
    def __init__(self):
        self.param_schema_definition = None
        self.url = None
        self.method = None
        self.token = None
        self.api_key = None
        self.basic_auth = "{}"
        self.headers = "{}"
        self.params = "{}"
        self.body = "{}"
        self.function_name = None

    def _get_authorization_header(self):
        if self.api_key:
            return f"{self.api_key}"
        elif self.basic_auth:
            parsed_basic_auth = json.loads(self.basic_auth)
            if parsed_basic_auth.get("username") and parsed_basic_auth.get("password"):
                return basic_auth_str(
                    username=parsed_basic_auth["username"],
                    password=parsed_basic_auth["password"],
                )
        elif self.token:
            return f"Bearer {self.token}"

    @exception_handler
    @with_debug_logs(app_name="custom-http")
    def execute(self, **kwargs):
        return HttpRequestExecutor.execute(
            dynamic_parameter_json_schema=self.param_schema_definition,
            base_path_params="{}",
            base_headers=self.headers,
            base_query_params=self.params,
            base_body=self.body,
            base_url=self.url,
            method=self.method,
            header_overrides={
                "Authorization": self._get_authorization_header()
            },
            function_name=self.function_name,
            app_name="custom-http",
            **kwargs,
        )

    @staticmethod
    def prepare(data):
        builder = CustomHttpActionBuilder()
        return (
            builder.set_param_schema(data["param_schema_definition"])
            .set_url(data["url"])
            .set_method(data["method"])
            .set_token(data["token"])
            .set_api_key(data["api_key"])
            .set_basic_auth(data["basic_auth"])
            .set_headers(data.get("headers", "{}"))
            .set_params(data.get("query", "{}"))
            .set_body(data.get("body", "{}"))
            .set_function_name(data.get("function_name", None))
            .build()
        )
