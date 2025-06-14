#!/usr/bin/env python

import unittest
import tempfile
import json
import sys
from io import StringIO
from unittest.mock import patch

import sexp2json
import sexpdata


class TestSexp2Json(unittest.TestCase):
    def test_tojsonable_basic(self):
        """Test tojsonable converts basic types correctly"""
        # Test basic conversion
        result = sexp2json.tojsonable([1, 2, 3])
        self.assertEqual(list(result), [1, 2, 3])

        # Test with symbols (Symbol has value() method)
        symbol = sexpdata.Symbol("test")
        result = sexp2json.tojsonable([symbol])
        self.assertEqual(list(result), ["test"])

    def test_cli_default_args(self):
        """Test CLI with default arguments (no files)"""
        with patch("sys.argv", ["sexp2json.py"]):
            with patch("sexp2json.sexp2json") as mock_sexp2json:
                sexp2json.main([])
                mock_sexp2json.assert_called_once()
                args = mock_sexp2json.call_args[1]
                self.assertEqual(args["file"], [])
                # Default output goes to stdout (file descriptor or similar)
                self.assertTrue(hasattr(args["out"], "write"))

    def test_cli_with_output_file(self):
        """Test CLI with --out argument"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp_name = tmp.name

        try:
            with patch("sexp2json.sexp2json") as mock_sexp2json:
                sexp2json.main(["--out", tmp_name])
                mock_sexp2json.assert_called_once()
                args = mock_sexp2json.call_args[1]
                self.assertEqual(args["out"].name, tmp_name)
        finally:
            import os

            os.unlink(tmp_name)

    def test_cli_with_recursion_limit(self):
        """Test CLI with --recursionlimit argument"""
        with patch("sexp2json.sexp2json") as mock_sexp2json:
            sexp2json.main(["--recursionlimit", "2000"])
            mock_sexp2json.assert_called_once()
            args = mock_sexp2json.call_args[1]
            self.assertEqual(args["recursionlimit"], 2000)

    def test_sexp2json_function(self):
        """Test sexp2json function processes files correctly"""
        # Create test S-expression file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sexp", delete=False
        ) as sexp_file:
            sexp_file.write('(test "string" 123)')
            sexp_file_path = sexp_file.name

        try:
            # Capture output
            output = StringIO()

            # Process the file
            sexp2json.sexp2json([sexp_file_path], output, sys.getrecursionlimit())

            # Parse the JSON output
            output.seek(0)
            result = json.load(output)

            # Verify the conversion
            self.assertEqual(result, [["test", "string", 123]])

        finally:
            import os

            os.unlink(sexp_file_path)


if __name__ == "__main__":
    unittest.main()
