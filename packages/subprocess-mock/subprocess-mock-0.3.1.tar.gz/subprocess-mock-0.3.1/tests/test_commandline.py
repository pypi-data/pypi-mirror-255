# -*- coding: utf-8 -*-

"""

tests.test_commandline

Unit test the commandline module


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
import sys

from unittest import TestCase

from unittest.mock import patch

from subprocess_mock import commandline

from .commons import GenericCallResult, RETURNCODE_OK


class ExecResult(GenericCallResult):
    """Program execution result"""

    @classmethod
    def do_call(cls, *args, **kwargs):
        """Do the real function call"""
        program = commandline.Program(*args)
        return program.execute()


class Program(TestCase):
    """Test the Program class"""

    @patch("sys.argv", new=[sys.argv[0]])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_execute(self, mock_stdout: io.StringIO) -> None:
        """execute() method in debug mode, returncode only"""
        result = ExecResult.from_call("--debug", stdout=mock_stdout)
        self.assertEqual(result.returncode, RETURNCODE_OK)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_version(self, mock_stdout: io.StringIO) -> None:
        """execute() method, version output"""
        with self.assertRaises(SystemExit) as cmgr:
            commandline.Program("--version").execute()
        #
        self.assertEqual(cmgr.exception.code, RETURNCODE_OK)
        self.assertEqual(
            mock_stdout.getvalue().strip(),
            commandline.__version__,
        )


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
