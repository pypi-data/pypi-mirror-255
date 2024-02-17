import base64
import builtins
from typing import List, Optional
from oauth2client.client import AccessTokenCredentials
from googleapiclient.discovery import build
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

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class UpdatedRow(BaseModel):
    spreadsheet: str = Field(..., title="Spreadsheet")
    spreadsheet_url: str = Field(..., title="Spreadsheet URL")
    updated_range: str = Field(..., title="Updated Range")
    updated_rows: int = Field(..., title="Updated Rows")
    updated_columns: int = Field(..., title="Updated Columns")
    updated_cells: int = Field(..., title="Updated Cells")


class AddRowResponse(StradaResponse):
    def __init__(self, response):
        super().__init__(
            success=False, error=None, data=None
        )  # Initialize parent class attributes

        if response and "updates" in response:
            self.success = True
            self.data = UpdatedRow(
                spreadsheet=response["spreadsheetId"],
                spreadsheet_url=f"https://docs.google.com/spreadsheets/d/{response['spreadsheetId']}/edit#gid={response['tableRange']}",
                updated_range=response["updates"]["updatedRange"],
                updated_rows=response["updates"]["updatedRows"],
                updated_columns=response["updates"]["updatedColumns"],
                updated_cells=response["updates"]["updatedCells"],
            )
        else:
            self.error = StradaError(
                errorCode=200,
                statusCode=200,
                message="No data was returned from Google Sheets API. See full response in 'data' field.",
            )
            self.data = response

class AddRowRequestPayload(BaseModel):
    google_drive: Optional[str] = Field(None, title="Google Drive")
    spreadsheet: str = Field(..., title="Spreadsheet ID")
    sheet: str = Field(..., title="Sheet")
    row: List[str] = Field(..., title="Row")


class SheetsAddRowActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "GoogleSheetsAddRow"

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
            self._instance = SheetsAddRowAction()
        return self._instance


class SheetsAddRowAction:
    def __init__(self):
        self.param_schema_definition = None
        self.token = None
        self.function_name = None
        self.payload = "{}"

    def parse_if_valid(raw_payload):
        # Now validate the payload against the SendPromptRequestPayload schema
        try:
            return AddRowRequestPayload(**raw_payload)
        except ValidationError as e:
            raise StradaValidationException(
                str(e), schema=AddRowRequestPayload.schema(), data=raw_payload
            )

    @with_debug_logs(app_name="google-sheet")
    @exception_handler
    def execute(self, **kwargs):
        validate_http_input(self.param_schema_definition, **kwargs)

        raw_payload = hydrate_input_fields(
            self.param_schema_definition, self.payload, **kwargs
        )

        parsed_payload = SheetsAddRowAction.parse_if_valid(raw_payload)

        credentials = AccessTokenCredentials(self.token, "Strada-SDK")

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=credentials)

        # Prepare the new row data
        values = [
            list(parsed_payload.row)
        ]  # Convert to a 2D array as the API expects this format

        # Create the request body
        body = {"values": values}

        # Update the sheet
        sheet_range = f"{parsed_payload.sheet}!A1"  # Change this based on where you want to insert
        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=parsed_payload.spreadsheet,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",  # Use 'USER_ENTERED' if you want the values to be parsed by Sheets
            )
        )

        # Execute the request
        response = request.execute()
        return AddRowResponse(response)

    @staticmethod
    def prepare(data):
        builder = SheetsAddRowActionBuilder()
        return (
            builder.set_param_schema(data["param_schema_definition"])
            .set_token(data["access_token"])
            .set_payload(data["payload"])
            .set_function_name(data.get("function_name", None))
            .build()
        )


class AddRowActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, access_token):
        self._get_instance().credentials = AccessTokenCredentials(
            access_token, "Strada-SDK"
        )
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = AddRowAction()
        return self._instance


class AddRowAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, *args):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=self.credentials)

        # Prepare the new row data
        values = [list(args)]  # Convert to a 2D array as the API expects this format

        # Create the request body
        body = {"values": values}

        # Update the sheet
        sheet_range = (
            f"{self.sheet_id}!A1"  # Change this based on where you want to insert
        )
        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",  # Use 'USER_ENTERED' if you want the values to be parsed by Sheets
            )
        )

        # Execute the request
        response = request.execute()
        return response

    @staticmethod
    def prepare(data):
        builder = AddRowActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["access_token"])
            .build()
        )


class AddRowsBulkActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, access_token):
        self._get_instance().credentials = AccessTokenCredentials(
            access_token, "Strada-SDK"
        )
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = AddRowsBulkAction()
        return self._instance


class AddRowsBulkAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, rows):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        service = build("sheets", "v4", credentials=self.credentials)

        # Prepare the new row data
        values = rows  # Assumes rows is a 2D array

        # Create the request body
        body = {"values": values}

        sheet_range = f"{self.sheet_id}!A1"

        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",
            )
        )

        response = request.execute()
        return response

    @staticmethod
    def prepare(data):
        builder = AddRowsBulkActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["access_token"])
            .build()
        )


class UpdateRowActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, access_token):
        self._get_instance().credentials = AccessTokenCredentials(
            access_token, "Strada-SDK"
        )
        return self

    def set_credentials(self, access_token):
        self._get_instance().credentials = AccessTokenCredentials(
            access_token, "Strada-SDK"
        )
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = UpdateRowAction()
        return self._instance


class UpdateRowAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, row_number, *args):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=self.credentials)

        # Prepare the new row data
        values = [list(args)]

        # Create the request body
        body = {"values": values}

        # Update the sheet
        sheet_range = f"{self.sheet_id}!A{row_number}"
        request = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",
            )
        )

        # Execute the request
        response = request.execute()
        return response

    @staticmethod
    def prepare(data):
        builder = UpdateRowActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["access_token"])
            .build()
        )


class GetRowsActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, access_token):
        self._get_instance().credentials = AccessTokenCredentials(
            access_token, "Strada-SDK"
        )
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = GetRowsAction()
        return self._instance


class GetRowsAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, starting_row_number: int, ending_row_number: int):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=self.credentials)

        # Define the range to fetch rows
        sheet_range = f"{self.sheet_id}!A{starting_row_number}:Z{ending_row_number}"

        # Fetch rows from Google Sheet
        request = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
            )
        )

        # Execute the request
        response = request.execute()
        return response.get("values", [])

    @staticmethod
    def prepare(data):
        builder = GetRowsActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["access_token"])
            .build()
        )


class SheetsCustomHttpActionBuilder:
    def __init__(self):
        self._instance = None
        self.default_function_name = "GoogleSheetsAction"

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
            self._instance = SheetsCustomHttpAction()
        return self._instance


class SheetsCustomHttpAction:
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

    @with_debug_logs(app_name="google-sheet")
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
                "Content-Type": "application/json",
            },
            function_name=self.function_name,
            app_name="google-sheet",
            **kwargs,
        )

    @staticmethod
    def prepare(data):
        builder = SheetsCustomHttpActionBuilder()
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
