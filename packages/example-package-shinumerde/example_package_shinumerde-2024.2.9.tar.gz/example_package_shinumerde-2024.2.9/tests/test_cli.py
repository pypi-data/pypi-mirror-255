import sys
import unittest
from unittest.mock import patch, mock_open

from parameterized import parameterized

from prog import main


class TestCli(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data='abcd'))
    def test_mock_file(self):
        sys.argv = ['prog.py', '--file', 'file']
        self.assertEqual(main(), 4)

    @parameterized.expand([
        ("abcd", 4),
        ("a", 1),
        ("dffcv", 3)
    ])
    def test_string(self, char, expected):
        sys.argv = ['prog.py', '--string', char]
        self.assertEqual(main(), expected)

    @patch('builtins.open', mock_open(read_data='abcdef'))
    def test_file_before_string(self):
        sys.argv = ['prog.py', '--string', 'a', '--file', 'file']
        self.assertEqual(main(), 6)

    def test_empty_string(self):
        sys.argv = ['prog.py', '--string', " "]
        self.assertEqual(main(), 1)
