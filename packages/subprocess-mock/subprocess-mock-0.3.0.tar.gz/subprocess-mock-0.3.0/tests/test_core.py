# -*- coding: utf-8 -*-

"""

tests.test_core

Unit test the functions module


Copyright (C) 2024 Rainer Schwarzbach

This file is part of subprocess-mock.

subprocess-mock is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

subprocess-mock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import io
import pathlib
import subprocess
import sys
import tempfile


from unittest import TestCase

from unittest.mock import patch

from subprocess_mock import commons
from subprocess_mock import child
from subprocess_mock import functions


SUBPROCESS_RUN = "subprocess.run"
SYS_STDOUT = "sys.stdout"
SYS_STDERR = "sys.stderr"
ECHO_COMMAND = "echo"


class ModuleFunctions(TestCase):
    """Test the functions"""

    maxDiff = None

    # pylint: disable=protected-access

    def test_run(self) -> None:
        """run() function"""
        with tempfile.TemporaryDirectory() as tempdir:
            new_file_path = pathlib.Path(tempdir) / "new_file.txt"
            with self.subTest("file does not pre-exist"):
                self.assertFalse(new_file_path.exists())
            #
            msg_prefix = "Non-mocked call:"
            with self.subTest(f"{msg_prefix} file does not pre-exist"):
                self.assertFalse(new_file_path.exists())
            #
            touch_command = ["touch", str(new_file_path)]
            result = subprocess.run(touch_command, check=False)
            with self.subTest(f"{msg_prefix} {commons.KW_RETURNCODE}"):
                self.assertEqual(result.returncode, commons.RETURNCODE_OK)
            #
            with self.subTest(
                f"{msg_prefix} mock call result was not registered"
            ):
                self.assertEqual(functions._CALL_RESULTS, [])
            #
            with self.subTest(f"{msg_prefix} file does post-exist"):
                self.assertTrue(new_file_path.exists())
            #
            new_file_path.unlink()
            with patch(SUBPROCESS_RUN, new=functions.run):
                touch_command = ["touch", str(new_file_path)]
                child.MockedProcess.add_program(
                    child.WriteOutput("program output"),
                    child.WriteError("error data\n"),
                )
                result = subprocess.run(
                    touch_command,
                    stdout=subprocess.PIPE,
                    stderr=None,
                    check=False,
                )
                with self.subTest("call arguments"):
                    self.assertEqual(result.args, touch_command)
                #
                with self.subTest(commons.KW_RETURNCODE):
                    self.assertEqual(result.returncode, commons.RETURNCODE_OK)
                #
                with self.subTest(commons.KW_STDOUT):
                    self.assertEqual(result.stdout, b"program output")
                #
                with self.subTest(commons.KW_STDERR):
                    self.assertIsNone(result.stderr)
                #
                with self.subTest("mock call result was registered"):
                    last_result = functions._CALL_RESULTS[-1]
                    self.assertIs(result, last_result[0])
                #
                with self.subTest("file does not post-exist"):
                    self.assertFalse(new_file_path.exists())
                #
            #
        #

    def test_run_unsuccessful(self) -> None:
        """run() function - unsuccessful execution"""
        command = ["false"]
        child.MockedProcess.add_program(
            child.SetReturncode(commons.RETURNCODE_ERROR)
        )
        self.assertRaises(
            subprocess.CalledProcessError,
            subprocess.run,
            command,
            check=True,
        )

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_run_stdout(self, mock_stderr: io.StringIO) -> None:
        """run() function with output to stdout only"""
        with patch(SUBPROCESS_RUN, new=functions.run):
            output_data = "foo bar 1"
            error_data = "error data 1"
            command = [ECHO_COMMAND, output_data]
            child.MockedProcess.add_program(
                child.WriteOutput(output_data),
                child.WriteError(error_data),
            )
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=None,
                check=False,
            )
            with self.subTest("call arguments"):
                self.assertEqual(result.args, command)
            #
            with self.subTest(commons.KW_RETURNCODE):
                self.assertEqual(result.returncode, commons.RETURNCODE_OK)
            #
            with self.subTest(commons.KW_STDOUT):
                self.assertEqual(result.stdout, output_data.encode())
            #
            with self.subTest(commons.KW_STDERR):
                self.assertIsNone(result.stderr)
            #
            with self.subTest("mock call result was registered"):
                last_result = functions._CALL_RESULTS[-1]
                self.assertIs(result, last_result[0])
            #
        #
        with self.subTest("mock_stderr is sys.stderr"):
            self.assertIs(mock_stderr, sys.stderr)
        #
        # with self.subTest(f"{commons.KW_STDERR} going to sys.stderr"):
        #    self.assertEqual(mock_stderr.getvalue(), error_data)
        #

    def test_run_filter(self) -> None:
        """run() function with filtering input"""
        # pylint: disable=unreachable
        with patch(SUBPROCESS_RUN, new=functions.run):
            input_data = b"Please Swap Case"
            expected_result = b"pLEASE sWAP cASE"
            command = ["tr", "whatever"]
            child.MockedProcess.add_program(child.Filter(str.swapcase))
            result = subprocess.run(
                command,
                input=input_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            with self.subTest("call arguments"):
                self.assertEqual(result.args, command)
            #
            with self.subTest(commons.KW_RETURNCODE):
                self.assertEqual(result.returncode, commons.RETURNCODE_OK)
            #
            with self.subTest(commons.KW_STDOUT):
                self.assertEqual(result.stdout, expected_result)
            #
            with self.subTest(commons.KW_STDERR):
                self.assertEqual(result.stderr, b"")
            #
            with self.subTest("mock call result was registered"):
                last_result = functions._CALL_RESULTS[-1]
                self.assertIs(result, last_result[0])
            #
        #

    @patch(
        "subprocess_mock.functions.parent.child.sys.stdout",
        new_callable=io.StringIO,
    )
    def test_run_stderr(self, mock_stdout: io.StringIO) -> None:
        """run() function with output to stderr only"""
        with patch(SUBPROCESS_RUN, new=functions.run):
            output_data = "foo bar 2"
            error_data = "error data 2"
            command = [ECHO_COMMAND, output_data]
            child.MockedProcess.add_program(
                child.WriteOutput(output_data),
                child.WriteError(error_data),
            )
            result = subprocess.run(
                command,
                stdout=None,
                stderr=subprocess.PIPE,
                check=False,
            )
            with self.subTest("call arguments"):
                self.assertEqual(result.args, command)
            #
            with self.subTest(commons.KW_RETURNCODE):
                self.assertEqual(result.returncode, commons.RETURNCODE_OK)
            #
            with self.subTest(commons.KW_STDOUT):
                self.assertIsNone(result.stdout)
            #
            with self.subTest(commons.KW_STDERR):
                self.assertEqual(result.stderr, error_data.encode())
            #
            with self.subTest("mock call result was registered"):
                last_result = functions._CALL_RESULTS[-1]
                self.assertIs(result, last_result[0])
            #
            with self.subTest("mock_stdout is sys.stdout"):
                self.assertIs(mock_stdout, sys.stdout)
            #
            # with self.subTest(f"{commons.KW_STDOUT} going to sys.stdout"):
            #     self.assertEqual(mock_stdout.getvalue(), output_data)
            #
        #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
