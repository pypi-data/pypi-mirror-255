import base64
import boto3
from pydantic import BaseModel, Field, ValidationError

from ..custom_types import StradaError, StradaResponse
from ..exception import StradaValidationException
from ..debug_logger import with_debug_logs
from ..sdk import HttpRequestExecutor
from ..exception_handler import exception_handler
from ..common import (
    build_input_schema_from_strada_param_definitions,
    hydrate_input_fields,
    validate_http_input,
)

class SendEmailRequestPayload(BaseModel):
    source: str = Field(..., title="Sender")
    to: str = Field(..., title="To")
    subject: str = Field(..., title="Subject")
    message: str = Field(..., title="Message")


class SendEmailActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "SesSendEmail"

    def set_param_schema(self, param_schema):
        self._get_instance().param_schema_definition = (
            build_input_schema_from_strada_param_definitions(param_schema)
        )
        return self

    def set_role_arn(self, customer_role_arn):
        self._get_instance().customer_role_arn = customer_role_arn
        return self

    def set_payload(self, row_data_json: str):
        decoded = base64.b64decode(row_data_json).decode("utf-8")
        self._get_instance().payload = decoded
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
            self._instance = SendEmailAction()
        return self._instance

class SendEmailResponse(StradaResponse):
    def __init__(self, result, error : Exception =None):
        super().__init__(
            success=False, error=None, data=None
        )  # Initialize parent class attributes

        if error:
            self.error = StradaError(
                errorCode=400,
                statusCode=400,
                message=str(error)
            ) 
        else:
            data = result
    


class SendEmailAction:
    def __init__(self):
        self.param_schema_definition = None
        self.customer_role_arn = None
        self.function_name = None
        self.payload = "{}"

    def parse_if_valid(raw_payload):
        # Now validate the payload against the SendPromptRequestPayload schema
        try:
            return SendEmailRequestPayload(**raw_payload)
        except ValidationError as e:
            raise StradaValidationException(
                str(e), schema=SendEmailRequestPayload.schema(), data=raw_payload
            )

    @with_debug_logs(app_name="aws-ses")
    @exception_handler
    def execute(self, **kwargs):
        validate_http_input(self.param_schema_definition, **kwargs)

        raw_payload = hydrate_input_fields(
            self.param_schema_definition, self.payload, **kwargs
        )

        parsed_payload = SendEmailAction.parse_if_valid(raw_payload)
        sts_client = boto3.client("sts")
        response = sts_client.assume_role(
            RoleArn=self.customer_role_arn,
            RoleSessionName="strada_send_email_action",
        )

        credentials = response["Credentials"]

        ses_client = boto3.client(
            "ses",
            region_name="us-east-1",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )

        try:
            response = ses_client.send_email(
                Source=parsed_payload.source,
                Destination={
                    "ToAddresses": [
                        parsed_payload.to,
                    ]
                },
                Message={
                    "Subject": {"Data": parsed_payload.subject, "Charset": "UTF-8"},
                    "Body": {"Text": {"Data": parsed_payload.message, "Charset": "UTF-8"}},
                },
            )

            return SendEmailResponse(result=response)
        except Exception as e:
            if hasattr(e, "response"):
                return SendEmailResponse(result=e.response['Error'], error=e) 
            else:
                return SendEmailResponse(result=None, error=e)

    @staticmethod
    def prepare(data):
        builder = SendEmailActionBuilder()
        return (
            builder.set_param_schema(data["param_schema_definition"])
            .set_role_arn(data["role_arn"])
            .set_payload(data["payload"])
            .set_function_name(data.get("function_name", None))
            .build()
        )


class SesCustomHttpActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "AmazonSESAction"

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
            self._instance = SesCustomHttpAction()
        return self._instance


class SesCustomHttpAction:
    def __init__(self):
        self.param_schema_definition = None
        self.url = None
        self.method = None
        self.token = None
        self.headers = "{}"
        self.params = "{}"
        self.body = "{}"
        self.function_name = None

    @with_debug_logs(app_name="aws-ses")
    @exception_handler
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
                "Authorization": f"{self.token}",
                "Content-Type": "application/json",
            },
            function_name=self.function_name,
            app_name="aws-ses",
            **kwargs,
        )

    @staticmethod
    def prepare(data):
        builder = SesCustomHttpActionBuilder()
        return (
            builder.set_param_schema(data["param_schema_definition"])
            .set_url(data["url"])
            .set_method(data["method"])
            .set_token(data["api_key"])
            .set_headers(data.get("headers", "{}"))
            .set_params(data.get("params", "{}"))
            .set_body(data.get("body", "{}"))
            .set_function_name(data.get("function_name", None))
            .build()
        )