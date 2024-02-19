import unittest
import json
from unittest.mock import patch
from strada.common import (
    fill_path_params,
    build_input_schema_from_strada_param_definitions,
    validate_http_input,
    basic_auth_str,
)
from strada.exception import StradaValidationException
from strada.rest import CustomHttpAction


class TestCommon(unittest.TestCase):
    def test_fill_path_params(self):
        url = "http://example.com/resource/{id}"
        params = {"id": "123"}
        expected_url = "http://example.com/resource/123"
        self.assertEqual(fill_path_params(url, params), expected_url)

    def test_build_input_schema(self):
        param_definitions_str = json.dumps(
            [
                {"paramName": "name", "paramType": "string", "defaultValue": "Doe"},
                {"paramName": "age", "paramType": "number", "defaultValue": 30},
            ]
        )
        schema = build_input_schema_from_strada_param_definitions(param_definitions_str)
        expected_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "default": "Doe"},
                "age": {"type": "number", "default": 30},
            },
            "required": ["name", "age"],
        }
        self.assertEqual(schema, expected_schema)

    def test_validate_http_input(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name"],
        }
        valid_input = {"name": "John", "age": 30}
        invalid_input = {"age": "thirty"}
        invalid_number_input = {"name": "John", "age": "thirty"}

        # Test valid input
        result, message = validate_http_input(schema, **valid_input)
        self.assertTrue(result)

        # Test invalid input
        with self.assertRaises(StradaValidationException) as context:
            validate_http_input(schema, **invalid_input)
        exception = context.exception
        self.assertEqual(exception.schema, schema)
        self.assertEqual(exception.data, invalid_input)
        self.assertIn("required property", str(exception))

        # Test invalid number input
        with self.assertRaises(StradaValidationException) as context:
            validate_http_input(schema, **invalid_number_input)
        exception = context.exception
        self.assertEqual(exception.schema, schema)
        self.assertEqual(exception.data, invalid_number_input)
        self.assertIn("is not of type 'number'", str(exception))


class TestAuthorizationHeader(unittest.TestCase):
    def test_with_api_key(self):
        instance = CustomHttpAction()
        instance.api_key = "api_key_value"
        instance.basic_auth = None
        instance.token = None

        self.assertEqual(instance._get_authorization_header(), "api_key_value")

    def test_with_basic_auth(self):
        instance = CustomHttpAction()
        instance.api_key = None
        instance.basic_auth = json.dumps({"username": "user", "password": "pass"})
        instance.token = None

        expected_auth = basic_auth_str("user", "pass")
        self.assertEqual(instance._get_authorization_header(), expected_auth)
    
    def test_with_basic_auth_missing_username(self):
        instance = CustomHttpAction()
        instance.api_key = None
        instance.basic_auth = json.dumps({"password": "pass"})
        instance.token = None

        expected_auth = None 
        self.assertEqual(instance._get_authorization_header(), expected_auth)

    def test_with_basic_auth_missing_username(self):
        instance = CustomHttpAction()
        instance.api_key = None
        instance.basic_auth = json.dumps({"username": "user"})
        instance.token = None

        expected_auth = None 
        self.assertEqual(instance._get_authorization_header(), expected_auth)

    def test_with_token(self):
        instance = CustomHttpAction()
        instance.api_key = None
        instance.basic_auth = None
        instance.token = "token_value"

        self.assertEqual(instance._get_authorization_header(), "Bearer token_value")

    # Optionally, a test to ensure it returns None if none of the auth methods are set
    def test_without_auth(self):
        instance = CustomHttpAction()
        instance.api_key = None
        instance.basic_auth = None
        instance.token = None

        self.assertIsNone(instance._get_authorization_header())


if __name__ == "__main__":
    unittest.main()
