import unittest
from unittest.mock import patch, MagicMock
from strada.sdk import HttpRequestExecutor
from strada.custom_types import StradaResponse, StradaError



class TestHttpRequestExecutor(unittest.TestCase):
    @patch("requests.request")
    @patch("strada.common.validate_http_input")
    @patch("strada.common.hydrate_input_fields")
    @patch("strada.common.fill_path_params")
    def test_execute_success(
        self,
        mock_fill_path_params,
        mock_hydrate_input_fields,
        mock_validate_http_input,
        mock_request,
    ):
        # Setup
        mock_request.return_value = MagicMock(
            ok=True, json=lambda: {"some": "data"}, status_code=200
        )
        mock_hydrate_input_fields.side_effect = lambda schema, base, **kwargs: base
        mock_fill_path_params.return_value = "https://example.com"

        # Execute
        response = HttpRequestExecutor.execute(
            dynamic_parameter_json_schema="{}",
            base_path_params="{}",
            base_headers="{}",
            base_query_params="{}",
            base_body="{}",
            base_url="https://example.com",
            method="GET",
        )

        # Assert
        self.assertIsInstance(response, StradaResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.data, {"some": "data"})
        mock_request.assert_called_once()

    @patch("strada.common.validate_http_input")
    @patch("strada.common.hydrate_input_fields")
    @patch("strada.common.fill_path_params")
    def test_utility_function_calls(
        self, mock_fill_path_params, mock_hydrate_input_fields, mock_validate_http_input
    ):
        HttpRequestExecutor.execute(
            dynamic_parameter_json_schema="{}",
            base_path_params="{}",
            base_headers="{}",
            base_query_params="{}",
            base_body="{}",
            base_url="https://example.com",
            method="GET",
        )

        mock_validate_http_input.assert_called_once()
        self.assertEqual(mock_hydrate_input_fields.call_count, 4)
        mock_fill_path_params.assert_called_once_with("https://example.com", "{}")

    @patch("requests.request")
    def test_execute_with_invalid_input(self, mock_request):
        mock_request.return_value = MagicMock(
            ok=False, json=lambda: {"message": "Invalid input"}, status_code=400
        )

        response = HttpRequestExecutor.execute(
            dynamic_parameter_json_schema="{}",
            base_path_params="{}",
            base_headers="{}",
            base_query_params="{}",
            base_body="{}",
            base_url="https://invalid_url",
            method="GET",
        )

        self.assertFalse(response.success)
        self.assertEqual(response.error.statusCode, 400)
        self.assertEqual(response.error.message, "Invalid input")

    @patch("requests.request")
    def test_execute_with_header_overrides(self, mock_request):
        mock_request.return_value = MagicMock(
            ok=True, json=lambda: {"some": "data"}, status_code=200
        )

        header_overrides = {"Authorization": "Bearer token123"}
        response = HttpRequestExecutor.execute(
            dynamic_parameter_json_schema="{}",
            base_path_params="{}",
            base_headers="{}",
            base_query_params="{}",
            base_body="{}",
            base_url="https://example.com",
            method="GET",
            header_overrides=header_overrides,
        )

        self.assertTrue(
            all(
                item in mock_request.call_args[1]["headers"].items()
                for item in header_overrides.items()
            )
        )


    @patch('requests.request')
    def test_execute_with_different_response_codes(self, mock_request):
        for status_code in [400, 401, 403, 404, 500]:
            mock_request.return_value = MagicMock(ok=False, json=lambda: {"message": "Some error"}, status_code=status_code)

            response = HttpRequestExecutor.execute(
                dynamic_parameter_json_schema="{}",
                base_path_params="{}",
                base_headers="{}",
                base_query_params="{}",
                base_body="{}",
                base_url='https://example.com',
                method='GET'
            )

            self.assertIsInstance(response, StradaResponse)
            self.assertFalse(response.success)
            self.assertEqual(response.error.statusCode, status_code)
            self.assertEqual(response.error.message, "Some error")
