# -*- coding: utf-8 -*-

"""

subprocess_mock.commandline

Command line functionality


Copyright (C) 2024 Rainer Schwarzbach

This file is part of subprocess-mock.

subprocess-mock is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

subprocess-mock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import argparse
import logging

from subprocess_mock import __version__


#
# Constants
#


RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


#
# classes
#


class Program:
    """Command line program"""

    name: str = "subprocess_mock"
    description: str = (
        "Mock objects for the standard library’s subprocess module"
    )

    def __init__(self, *args: str) -> None:
        """Parse command line arguments and initialize the logger

        :param args: a list of command line arguments
        """
        self.__arguments = self._parse_args(*args)
        if self.arguments.loglevel < logging.DEBUG:
            message_format = (
                "%(levelname)-8s | (%(funcName)s:%(lineno)s) %(message)s"
            )
        else:
            message_format = "%(levelname)-8s | %(message)s"
        #
        logging.basicConfig(
            format=message_format,
            level=self.arguments.loglevel,
        )

    @property
    def arguments(self) -> argparse.Namespace:
        """Property: command line arguments

        :returns: the parsed command line arguments
        """
        return self.__arguments

    def _parse_args(self, *args: str) -> argparse.Namespace:
        """Parse command line arguments using argparse
        and return the arguments namespace.

        :param args: the command line arguments
        :returns: the parsed command line arguments as returned
            by argparse.ArgumentParser().parse_args()
        """
        main_parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
        )
        main_parser.set_defaults(loglevel=logging.WARNING)
        main_parser.add_argument(
            "--version",
            action="version",
            version=__version__,
            help="print version and exit",
        )
        logging_group = main_parser.add_argument_group(
            "Logging options", "control log level (default is WARNING)"
        )
        verbosity_mutex = logging_group.add_mutually_exclusive_group()
        verbosity_mutex.add_argument(
            "-d",
            "--debug",
            action="store_const",
            const=logging.DEBUG,
            dest="loglevel",
            help="output all messages (log level DEBUG)",
        )
        verbosity_mutex.add_argument(
            "-v",
            "--verbose",
            action="store_const",
            const=logging.INFO,
            dest="loglevel",
            help="be more verbose (log level INFO)",
        )
        verbosity_mutex.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=logging.ERROR,
            dest="loglevel",
            help="be more quiet (log level ERROR)",
        )
        return main_parser.parse_args(args=args or None)

    def execute(self) -> int:
        """Execute the program
        :returns: the returncode for the script
        """
        return RETURNCODE_OK


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
