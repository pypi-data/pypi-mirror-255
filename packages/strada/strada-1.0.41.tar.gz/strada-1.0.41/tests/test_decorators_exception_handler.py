import unittest
from unittest.mock import patch

from strada.exception_handler import exception_handler
from strada.exception import StradaValidationException


class TestExceptionHandlerDecorator(unittest.TestCase):
    def setUp(self):
        class TestClass:
            @exception_handler
            def test_method(self, exception_instance=None):
                if exception_instance:
                    raise exception_instance
                return "No exception"

        self.test_class_instance = TestClass()

    @patch("builtins.print")
    def test_exception_handler_with_custom_exception(self, mock_print):
        custom_exception = StradaValidationException(
            message="Test \n exception \n message",
            schema="Test schema",
            data="Test data",
        )
        self.test_class_instance.test_method(exception_instance=custom_exception)

        # Adjust the expected message to match the output format
        expected_message = "[Error] TestClass.test_method:\n\t Test \n\t exception \n\t message - Schema: Test schema, Data: Test data"
        mock_print.assert_called_with(expected_message)

    @patch("builtins.print")
    def test_exception_handler_with_generic_exception(self, mock_print):
        generic_exception = Exception("Test exception message")
        self.test_class_instance.test_method(exception_instance=generic_exception)

        expected_message = "[Error] TestClass.test_method:\n\t Test exception message"
        mock_print.assert_called_with(expected_message)

    def test_no_exception(self):
        result = self.test_class_instance.test_method(exception_instance=None)
        self.assertEqual(result, "No exception")


if __name__ == "__main__":
    unittest.main()
