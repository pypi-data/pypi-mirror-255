import unittest
import json
from unittest.mock import patch
from strada.common import hydrate_input_fields


class TestHydration(unittest.TestCase):
    def setUp(self):
        self.input_schema = {
            "type": "object",
            "properties": {
                "emailCount": {"type": "number"},
                "isActive": {"type": "boolean"},
                "tags": {"type": "array"},
                "profile": {"type": "object"},
            },
            "required": ["emailCount"],
        }
        self.form_data_json_str = json.dumps(
            {
                "text": "New emails: {{emailCount}}, Active: {{isActive}}, Tags: {{tags}}, Profile: {{profile}}",
                "channel": "slack-test",
            }
        )

    def test_valid_values(self):
        kwargs = {
            "emailCount": 10,
            "isActive": True,
            "tags": '["urgent", "new"]',
            "profile": '{"name": "John Doe"}',
        }
        expected_result = {
            "text": 'New emails: 10, Active: true, Tags: ["urgent","new"], Profile: {"name":"John Doe"}',
            "channel": "slack-test",
        }
        result = hydrate_input_fields(
            self.input_schema, self.form_data_json_str, **kwargs
        )
        self.assertEqual(result, expected_result)

    def test_no_placeholders(self):
        form_data_json_str = '{"text":"No placeholders","channel":"slack-test"}'
        kwargs = {"emailCount": 10}
        expected_result = {
            "text": "No placeholders",
            "channel": "slack-test",
        }
        result = hydrate_input_fields(self.input_schema, form_data_json_str, **kwargs)
        self.assertEqual(result, expected_result)

    def test_incorrect_type_in_kwargs(self):
        kwargs = {"emailCount": "ten"}  # emailCount should be a number
        with self.assertRaises(ValueError):
            hydrate_input_fields(self.input_schema, self.form_data_json_str, **kwargs)

    def test_preserved_non_placeholder_text(self):
        form_data_json_str = (
            '{"text":"No placeholders here {{emailCount}}","channel":"slack-test"}'
        )
        kwargs = {"emailCount": 10}
        expected_result = {
            "text": "No placeholders here 10",
            "channel": "slack-test",
        }
        result = hydrate_input_fields(self.input_schema, form_data_json_str, **kwargs)
        self.assertEqual(result, expected_result)

    def test_some_values_passed_in(self):
        input_schema = {
            "type": "object",
            "properties": {"emailCount": {"type": "number"}},
            "required": ["emailCount"],
        }
        form_data_json_str = (
            '{"text":"New emails are {{emailCount}}","channel":"slack-test"}'
        )
        kwargs = {"emailCount": 10}
        expected_result = {
            "text": "New emails are 10",
            "channel": "slack-test",
        }
        result = hydrate_input_fields(input_schema, form_data_json_str, **kwargs)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
