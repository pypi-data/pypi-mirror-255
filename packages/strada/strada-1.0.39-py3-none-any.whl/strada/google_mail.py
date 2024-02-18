import base64
import builtins
from email.parser import BytesParser
import json
from typing import List 
from oauth2client.client import AccessTokenCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError, TransportError

from pydantic import BaseModel, Field, ValidationError
from .custom_types import StradaError, StradaResponse
from .exception import StradaValidationException
from .sdk import HttpRequestExecutor
from .exception_handler import exception_handler
from .common import (
    build_input_schema_from_strada_param_definitions,
    custom_print,
    hydrate_input_fields,
    validate_http_input,
)
from .debug_logger import with_debug_logs

# Initialize the print function to use the logger
builtins.print = custom_print


class UpdatedRow(BaseModel):
    spreadsheet: str = Field(..., title="Spreadsheet")
    spreadsheet_url: str = Field(..., title="Spreadsheet URL")
    updated_range: str = Field(..., title="Updated Range")
    updated_rows: int = Field(..., title="Updated Rows")
    updated_columns: int = Field(..., title="Updated Columns")
    updated_cells: int = Field(..., title="Updated Cells")


class GmailEmail(BaseModel):
    id: str = Field(..., title="Email ID")
    sender: str = Field(..., title="Sender")
    recipients: List[str] = Field(..., title="Recipients")
    date: str = Field(..., title="Date")
    subject: str = Field(..., title="Subject")
    body: str = Field(..., title="Body")
    thread_id: str = Field(..., title="Thread ID")


class SearchResult(BaseModel):
    query: str = Field(..., title="Search Query")
    emails: List[GmailEmail] = Field(..., title="Emails")
    count: int = Field(..., title="Count")


class SearchEmailsResponse(StradaResponse):
    def __init__(self, response):
        super().__init__(
            success=False, error=None, data=None
        )  # Initialize parent class attributes

        if response and "updates" in response:
            self.success = True
            self.data = None
        else:
            self.error = StradaError(
                errorCode=200,
                statusCode=200,
                message="No data was returned from Google Sheets API. See full response in 'data' field.",
            )
            self.data = response


class SearchEmailsRequestPayload(BaseModel):
    query: str = Field(..., title="Search Query")


class GmailSearchEmailsActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "GmailSearchEmailsAction"

    def set_param_schema(self, param_schema):
        self._get_instance().param_schema_definition = (
            build_input_schema_from_strada_param_definitions(param_schema)
        )
        return self

    def set_token(self, access_token):
        self._get_instance().token = access_token
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
            self._instance = GmailSearchEmailsAction()
        return self._instance


class GmailSearchEmailsAction:
    def __init__(self):
        self.param_schema_definition = None
        self.token = None
        self.function_name = None
        self.payload = "{}"

    def parse_if_valid(raw_payload):
        try:
            return SearchEmailsRequestPayload(**raw_payload)
        except ValidationError as e:
            raise StradaValidationException(
                str(e), schema=SearchEmailsRequestPayload.schema(), data=raw_payload
            )
    def _get_email_text(msg):
        # Check if the email message is multipart
        if msg.is_multipart():
            # Iterate over each part
            for part in msg.walk():
                # Select only the text/plain parts
                if part.get_content_type() == 'text/plain':
                    return part.get_payload(decode=True).decode(part.get_content_charset('utf-8'))
        else:
            # For non-multipart, just return the payload
            if msg.get_content_type() == 'text/plain':
                return msg.get_payload(decode=True).decode(msg.get_content_charset('utf-8'))

        # Return an empty string if no text/plain part is found
        return ''


    def _get_email_details(message_id, service):
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="raw")
            .execute()
        )
        msg_raw = base64.urlsafe_b64decode(message["raw"].encode("utf-8"))
        msg = BytesParser().parsebytes(msg_raw)

        mail = GmailEmail(
            id=message_id,
            sender=msg.get("From"),
            recipients=msg.get("To", "").split(","),
            date=msg.get("Date"),
            subject=msg.get("Subject"),
            body=GmailSearchEmailsAction._get_email_text(msg),
            thread_id=message["threadId"],
        )
        return mail

    @with_debug_logs(app_name="google-mail")
    @exception_handler
    def execute(self, **kwargs):
        validate_http_input(self.param_schema_definition, **kwargs)

        raw_payload = hydrate_input_fields(
            self.param_schema_definition, self.payload, **kwargs
        )

        parsed_payload = GmailSearchEmailsAction.parse_if_valid(raw_payload)

        credentials = AccessTokenCredentials(self.token, "Strada-SDK")

        # Initialize the Sheets API client
        try:
            service = build("gmail", "v1", credentials=credentials)

            result = (
                service.users()
                .messages()
                .list(userId="me", q=parsed_payload.query, maxResults=10)
                .execute()
            )
            emails = [
                GmailSearchEmailsAction._get_email_details(msg["id"], service)
                for msg in result.get("messages", [])
            ]

            return StradaResponse(
                success=True,
                data=SearchResult(
                    query=parsed_payload.query, emails=emails, count=len(emails)
                ),
            )
        except HttpError as error:
            error_details = json.loads(error.content).get("error", {})
            return StradaResponse(
                success=False,
                error=StradaError(
                    errorCode=error.resp.status,
                    statusCode=error.status_code,
                    message=error_details.get("message", "No details available"),
                ),
            )
        except RefreshError as auth_error:
            return StradaResponse(
                success=False,
                error=StradaError(
                    errorCode=401,  # Unauthorized
                    statusCode=401,
                    message=f"Authentication refresh error: {auth_error}",
                ),
            )
        except TransportError as transport_error:
            return StradaResponse(
                success=False,
                error=StradaError(
                    errorCode=503,  # Service Unavailable
                    statusCode=503,
                    message=f"Transport error: {transport_error}",
                ),
            )
        except ValueError as ve:
            return StradaResponse(
                success=False,
                error=StradaError(
                    errorCode=400,  # Bad Request
                    statusCode=400,
                    message=f"Value error: {ve}",
                ),
            )
        except TypeError as te:
            return StradaResponse(
                success=False,
                error=StradaError(
                    errorCode=400,  # Bad Request
                    statusCode=400,
                    message=f"Type error: {te}",
                ),
            )

    @staticmethod
    def prepare(data):
        builder = GmailSearchEmailsActionBuilder()
        return (
            builder.set_param_schema(data["param_schema_definition"])
            .set_token(data["access_token"])
            .set_payload(data["payload"])
            .set_function_name(data.get("function_name", None))
            .build()
        )


class GmailCustomHttpActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "GmailAction"

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

    def set_path_params(self, path_params):
        self._instance.path = path_params
        return self

    def set_query_params(self, params):
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
            self._instance = GmailCustomHttpAction()
        return self._instance


class GmailCustomHttpAction:
    def __init__(self):
        self.param_schema_definition = None
        self.url = None
        self.method = None
        self.token = None
        self.headers = "{}"
        self.path = "{}"
        self.params = "{}"
        self.body = "{}"
        self.function_name = None

    @with_debug_logs(app_name="google-mail")
    @exception_handler
    def execute(self, **kwargs):
        return HttpRequestExecutor.execute(
            dynamic_parameter_json_schema=self.param_schema_definition,
            base_path_params=self.path,
            base_headers=self.headers,
            base_query_params=self.params,
            base_body=self.body,
            base_url=self.url,
            method=self.method,
            header_overrides={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            },
            function_name=self.function_name,
            app_name="google-mail",
            **kwargs,
        )

    @staticmethod
    def prepare(data):
        builder = GmailCustomHttpActionBuilder()
        return (
            builder.set_param_schema(data["param_schema_definition"])
            .set_url(data["url"])
            .set_method(data["method"])
            .set_token(data["access_token"])
            .set_path_params(data.get("path", "{}"))
            .set_headers(data.get("headers", "{}"))
            .set_query_params(data.get("query", "{}"))
            .set_body(data.get("body", "{}"))
            .set_function_name(data.get("function_name", None))
            .build()
        )