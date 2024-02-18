from base64 import b64encode
import builtins
import json
import jsonschema
import re

from pydantic import BaseModel, ValidationError
from .exception import StradaValidationException

original_print = builtins.print

def fill_path_params(url, path_params):
    for key, value in path_params.items():
        url = url.replace("{" + key + "}", value)

    return url

def find_schema_for_key(key, schema):
    return schema["properties"][key]

def replace_placeholders(value, schema, **inner_kwargs):
    placeholders = re.findall(r"\{\{(.*?)\}\}", value)
    for key in placeholders:
        if key in inner_kwargs:
            specific_schema = find_schema_for_key(key, schema)
            if "type" in specific_schema:
                key_type = specific_schema["type"]
                # TODO: this is quite hacky and implies that we can only allow for overrides of string 
                # So if there is an array or object type that is passed in, it must replace the entire Value
                # For example we can't yet do:
                # [{{arrayValue}}], it has to be {{array}}
                if key_type == "array":
                    value = json.loads(convert_value(inner_kwargs[key], key_type))
                # TODO: this is quite hacky and implies that we can only allow for overrides of string 
                elif key_type == "object":
                    value = json.loads(convert_value(inner_kwargs[key], key_type))
                else:
                    value = value.replace(
                        "{{" + key + "}}", convert_value(inner_kwargs[key], key_type)
                    )
    return value

def convert_value(value, keyType):
    if keyType == "number":
        return str(int(value))
    elif keyType == "boolean":
        return str(str(value).lower() in ["true", "1", "yes"]).lower()
    elif keyType == "array":
        if isinstance(value, list):
            return json.dumps(value)
        if isinstance(value, str):
            return json.dumps(value.split(","))
    elif keyType == "object":
        # Assuming the value is a JSON string
        return value
    elif keyType == "string":
        return value
    else:
        raise NotImplementedError(f"Type '{keyType}' not handled")

def hydrate_input_str(formDataStr, input_schema , **kwargs):
    return replace_placeholders(formDataStr, input_schema, **kwargs)

def hydrate_input_fields(input_schema, formDataJsonStr, **kwargs):
    loaded_form_data = json.loads(formDataJsonStr)

    def process_value(value, schema):
        if isinstance(value, dict):
            return {k: process_value(v, schema) for k, v in value.items()}
        elif isinstance(value, list):
            return [process_value(item, schema) for item in value]
        elif isinstance(value, str):
            return replace_placeholders(value, schema, **kwargs)
        else:
            return value

    return process_value(loaded_form_data, input_schema)


def build_input_schema_from_strada_param_definitions(param_definitions_json_str):
    # Create an empty JSON schema object
    json_schema = {"type": "object", "properties": {}, "required": []}

    param_definitions = json.loads(param_definitions_json_str)
    for param_definition in param_definitions:
        param_name = param_definition["paramName"]
        param_type = param_definition["paramType"]

        # Create a property definition for the parameter
        property_definition = {"type": param_type}

        # If the parameter has a defaultValue, add it to the schema
        if "defaultValue" in param_definition and param_definition["defaultValue"]:
            property_definition["default"] = param_definition["defaultValue"]

        # Add the property definition to the JSON schema
        json_schema["properties"][param_name] = property_definition

        json_schema["required"].append(param_name)

    return json_schema


def validate_http_input(inputSchema, **kwargs):
    """
    Validate HTTP input data against a JSON schema.

    Args:
        inputSchema (dict): JSON schema representing the expected structure of the input data.
        **kwargs: Arbitrary keyword arguments representing the input data.

    Returns:
        bool: True if the input data adheres to the schema, False otherwise.
        str: A message indicating the validation result.

    Example usage:
        schema = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "number"}
            },
            "required": ["param1"]
        }
        result, message = validate_http_input(schema, param1="Hello", param2=42)

    """
    if (kwargs is None) or (len(kwargs) == 0):
        return True, "No input data provided."

    # Convert the input schema to a JSON string
    input_schema_str = json.dumps(inputSchema)

    # Parse the JSON schema
    schema = json.loads(input_schema_str)

    # Validate the input data against the schema
    try:
        jsonschema.validate(instance=kwargs, schema=schema)
        return True, "Input data adheres to the schema."
    except jsonschema.exceptions.ValidationError as e:
        raise StradaValidationException(str(e), schema=inputSchema, data=kwargs)


def basic_auth_str(username, password):
    """Returns a Basic Auth string."""
    if isinstance(username, str):
        username = username.encode("latin1")

    if isinstance(password, str):
        password = password.encode("latin1")

    authstr = "Basic " + to_native_string(
        b64encode(b":".join((username, password))).strip()
    )

    return authstr


def to_native_string(string, encoding="ascii"):
    """Given a string object, regardless of type, returns a representation of
    that string in the native string type, encoding and decoding where
    necessary. This assumes ASCII unless told otherwise.
    """
    if isinstance(string, str):
        out = string
    else:
        out = string.decode(encoding)

    return out

def custom_print(*args, **kwargs):
    args = (f"<LOG>{arg}</LOG>" for arg in args)
    original_print(*args, **kwargs)

def parse_if_valid(raw_payload, model: BaseModel):
    # Now validate the payload against the SendPromptRequestPayload schema
    try:
        return model(**raw_payload)
    except ValidationError as e:
        raise StradaValidationException(
            str(e), schema=model.schema(), data=raw_payload
        )
