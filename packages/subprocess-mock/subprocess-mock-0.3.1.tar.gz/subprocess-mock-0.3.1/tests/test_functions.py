# -*- coding: utf-8 -*-

"""

tests.test_functions

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

import logging
import pathlib
import subprocess
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


class Run(TestCase):
    """Test the run() function"""

    maxDiff = None

    def test_filter(self) -> None:
        """Program filtering stdin"""
        # pylint: disable=unreachable
        with patch(SUBPROCESS_RUN, new=functions.run):
            input_data = "lower case"
            expected_result = "LOWER CASE"
            command = ["tr", "[:lower:]", "[:upper:]"]
            child.MockedProcess.add_program(child.Filter(str.upper))
            result = subprocess.run(
                command,
                input=input_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
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
                self.assertEqual(result.stderr, "")
            #
        #


class StoringRunner(TestCase):
    """Test the StoringRunner class"""

    maxDiff = None

    # pylint: disable=protected-access

    def test_run_filter(self) -> None:
        """.run() method – Program filtering stdin"""
        # pylint: disable=unreachable
        storing_runner = functions.StoringRunner()
        with patch(SUBPROCESS_RUN, new=storing_runner.run):
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
                last_result = storing_runner.get_last_result()
                self.assertIs(result, last_result[0])
            #
        #

    def test_run_vs_non_mocked(self) -> None:
        """.run() method – Mocked call compared to a non-mocked call"""
        with tempfile.TemporaryDirectory() as tempdir:
            storing_runner = functions.StoringRunner()
            storing_runner.clear()
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
                self.assertEqual(storing_runner.all_results, [])
            #
            with self.subTest(f"{msg_prefix} file does post-exist"):
                self.assertTrue(new_file_path.exists())
            #
            new_file_path.unlink()
            with patch(SUBPROCESS_RUN, new=storing_runner.run):
                touch_command = ["touch", str(new_file_path)]
                child.MockedProcess.add_program(
                    child.WriteOutput("program output"),
                    child.WriteError("error data\n"),
                )
                result = subprocess.run(
                    touch_command,
                    stdout=subprocess.PIPE,
                    stderr=None,
                    check=True,
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
                    last_result = storing_runner.get_last_result()
                    self.assertIs(result, last_result[0])
                #
                with self.subTest("file does not post-exist"):
                    self.assertFalse(new_file_path.exists())
                #
            #
        #
        #

    def test_set_returncode(self) -> None:
        """.run() method – Set returncode"""
        command = ["false"]
        child.MockedProcess.add_program(
            child.SetReturncode(commons.RETURNCODE_ERROR)
        )
        storing_runner = functions.StoringRunner()
        with patch(SUBPROCESS_RUN, new=storing_runner.run):
            with self.subTest(
                "Exception is raised with nonzero returncode and check=True"
            ):
                self.assertRaises(
                    subprocess.CalledProcessError,
                    subprocess.run,
                    command,
                    check=True,
                )
            #
            logging.warning("Results store: %r", storing_runner.all_results)
            last_result = storing_runner.get_last_result()
            with self.subTest("Result was registered"):
                self.assertEqual(last_result[0].args, command)
            #
            with self.subTest("Returncode was recorded"):
                self.assertEqual(
                    last_result[0].returncode, commons.RETURNCODE_ERROR
                )
            #
        #
        #

    def test_run_stdout_only(self) -> None:
        """.run() method – Output to stdout only"""
        storing_runner = functions.StoringRunner()
        with patch(SUBPROCESS_RUN, new=storing_runner.run):
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
                last_result = storing_runner.get_last_result()
                self.assertIs(result, last_result[0])
            #
        #

    def test_run_stderr_only(self) -> None:
        """.run() method – Output to stderr only"""
        storing_runner = functions.StoringRunner()
        with patch(SUBPROCESS_RUN, new=storing_runner.run):
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
                last_result = storing_runner.get_last_result()
                self.assertIs(result, last_result[0])
            #
        #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
