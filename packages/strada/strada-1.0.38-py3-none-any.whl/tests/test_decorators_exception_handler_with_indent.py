import unittest
from strada.exception_handler import with_indent


class TestWithIndent(unittest.TestCase):
    def test_single_line(self):
        input_str = "This is a single line."
        expected = "This is a single line."
        self.assertEqual(with_indent(input_str), expected)

    def test_multiple_lines(self):
        input_str = "First line.\nSecond line.\nThird line."
        expected = "First line.\n\tSecond line.\n\tThird line."
        self.assertEqual(with_indent(input_str), expected)

    def test_empty_string(self):
        input_str = ""
        expected = ""
        self.assertEqual(with_indent(input_str), expected)

    def test_newline_at_start(self):
        input_str = "\nStarts with newline."
        expected = "\n\tStarts with newline."
        self.assertEqual(with_indent(input_str), expected)

    def test_newline_at_end(self):
        input_str = "Ends with newline.\n"
        expected = "Ends with newline.\n\t"
        self.assertEqual(with_indent(input_str), expected)


if __name__ == "__main__":
    unittest.main()
