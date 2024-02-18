import base64
import boto3
from pydantic import BaseModel, Field, ValidationError

from .custom_types import StradaError, StradaResponse
from .exception import StradaValidationException
from .debug_logger import with_debug_logs
from .exception_handler import exception_handler
from .common import (
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
        self.default_function_name = "SendEmail"

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
    
    def set_region(self, region):
      self._get_instance().region = region
      return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = StradaSendEmailAction()
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
            self.data = result
    
class StradaSendEmailAction:
    def __init__(self):
        self.param_schema_definition = None
        self.customer_role_arn = None
        self.region = "us-east-1"
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

    @with_debug_logs(app_name="email-strada")
    @exception_handler
    def execute(self, **kwargs):
        validate_http_input(self.param_schema_definition, **kwargs)

        raw_payload = hydrate_input_fields(
            self.param_schema_definition, self.payload, **kwargs
        )

        parsed_payload = StradaSendEmailAction.parse_if_valid(raw_payload)
        sts_client = boto3.client("sts")
        response = sts_client.assume_role(
            RoleArn=self.customer_role_arn,
            RoleSessionName="strada_send_email_action",
        )

        credentials = response["Credentials"]

        ses_client = boto3.client(
            "ses",
            region_name=self.region,
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
            .set_region(data.get("region", None))
            .build()
        )