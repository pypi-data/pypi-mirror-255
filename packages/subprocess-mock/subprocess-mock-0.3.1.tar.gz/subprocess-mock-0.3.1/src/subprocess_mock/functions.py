# -*- coding: utf-8 -*-

"""

subprocess_mock.functions

Functions mocking subprocess standard library functions behavior

Original subprocess module:
    Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>

Mock modifications (c) 2024 by Rainer Schwarzbach

This file is part of subprocess-mock.

subprocess-mock is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

subprocess-mock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""

import logging
import subprocess

from typing import Any, Dict, List, Tuple, Union

from subprocess_mock import parent
from subprocess_mock import commons


__all__ = [
    "call",
    "check_call",
    "getstatusoutput",
    "getoutput",
    "check_output",
    "run",
    "StoringRunner",
]


def call(*popenargs, timeout=None, **kwargs):
    """Run command with arguments.  Wait for command to complete or
    timeout, then return the returncode attribute.

    See the call() method of the StoringRunner class below for details.
    """
    return StoringRunner().call(*popenargs, timeout=timeout, **kwargs)


def check_call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete.  If
    the exit code was zero then return, otherwise raise
    CalledProcessError.  The CalledProcessError object will have the
    return code in the returncode attribute.

    See the check_call() method of the StoringRunner class below for details.
    """
    return StoringRunner().check_call(*popenargs, **kwargs)


def check_output(*popenargs, timeout=None, **kwargs):
    r"""Run command with arguments and return its output.

    See the check_output() method of the StoringRunner class below
    for details.
    """
    return StoringRunner().check_output(*popenargs, timeout=timeout, **kwargs)


# pylint: disable=redefined-builtin
def run(*popenargs, input=None, timeout=None, check=False, **kwargs):
    """Run command with arguments and return a CompletedProcess instance.

    See the run() method of the StoringRunner class below for details.
    """
    return StoringRunner().run(
        *popenargs, input=input, timeout=timeout, check=check, **kwargs
    )


# pylint: disable=redefined-builtin

# Various tools for executing commands and looking at their output and status.
#


def getstatusoutput(cmd) -> Tuple[int, str]:
    """Return (exitcode, output) of executing cmd in a shell.

    See the getstatusoutput() method of the StoringRunner class below
    for details.
    """
    return StoringRunner().getstatusoutput(cmd)


def getoutput(cmd) -> str:
    """Return output (stdout or stderr) of executing cmd in a shell.

    See the getoutput() method of the StoringRunner class below for details.
    """
    return StoringRunner().getoutput(cmd)


# Class implementing the function calls


class StoringRunner:
    """Object which can start subprocesses and keeps a list of
    process results (ie. CompletedProcess instances)
    """

    def __init__(self) -> None:
        """Allocate the internal list"""
        self.__all_results: List[
            Tuple[subprocess.CompletedProcess, Dict[str, Any]]
        ] = []

    @property
    def all_results(
        self,
    ) -> List[Tuple[subprocess.CompletedProcess, Dict[str, Any]]]:
        """Property: the collected results list"""
        return list(self.__all_results)

    def add(self, result: subprocess.CompletedProcess, **kwargs) -> None:
        """add a result"""
        self.__all_results.append((result, kwargs))

    def clear(self) -> None:
        """clear results"""
        self.__all_results.clear()

    def get_last_result(
        self,
    ) -> Tuple[subprocess.CompletedProcess, Dict[str, Any]]:
        """return the last result"""
        return self.__all_results[-1]

    def call(self, *popenargs, timeout=None, **kwargs) -> int:
        """Run command with arguments.  Wait for command to complete or
        timeout, then return the returncode attribute.

        The arguments are the same as for the
        subprocess_mock.parent.Popen constructor.
        Example:

        retcode = call(["ls", "-l"])
        """
        with parent.Popen(*popenargs, **kwargs) as p:
            try:
                retcode = p.wait(timeout=timeout)
            except Exception as exc:
                p.kill()
                p.wait()
                raise exc
            #
            result: subprocess.CompletedProcess = subprocess.CompletedProcess(
                p.args, retcode, None, None
            )
            self.add(result)
            return retcode

    def check_call(self, *popenargs, **kwargs) -> int:
        """Run command with arguments.  Wait for command to complete.  If
        the exit code was zero then return, otherwise raise
        CalledProcessError.  The CalledProcessError object will have the
        return code in the returncode attribute.

        The arguments are the same as for the call function.  Example:

        check_call(["ls", "-l"])
        """
        retcode = self.call(*popenargs, **kwargs)
        if retcode:
            cmd = kwargs.get(commons.KW_ARGS)
            if cmd is None:
                cmd = popenargs[0]
            #
            raise subprocess.CalledProcessError(retcode, cmd)
        #
        return 0

    def check_output(
        self, *popenargs, timeout=None, **kwargs
    ) -> Union[bytes, str]:
        """Run command with arguments and return its output.

        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.

        The arguments are the same as for the Popen constructor.
        Example:

        >>> check_output(["ls", "-l", "/dev/null"])
        b'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.

        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        b'ls: non_existent_file: No such file or directory\n'

        There is an additional optional argument, "input", allowing you to
        pass a string to the subprocess's stdin.  If you use this argument
        you may not also use the Popen constructor's "stdin" argument, as
        it too will be used internally.
        Example:

        >>> check_output(["sed", "-e", "s/foo/bar/"],
        ...              input=b"when in the course of fooman events\n")
        b'when in the course of barman events\n'

        If universal_newlines=True is passed, the "input" argument must be a
        string and the return value will be a string rather than bytes.
        """
        if commons.KW_STDOUT in kwargs:
            raise ValueError(
                "stdout argument not allowed, it will be overridden."
            )

        if "input" in kwargs and kwargs["input"] is None:
            # Explicitly passing input=None was previously equivalent
            # to passing an empty string.
            # That is maintained here for backwards compatibility.
            kwargs["input"] = (
                "" if kwargs.get("universal_newlines", False) else b""
            )

        return self.run(
            *popenargs,
            stdout=commons.PIPE,
            timeout=timeout,
            check=True,
            **kwargs,
        ).stdout

    def getstatusoutput(self, cmd) -> Tuple[int, str]:
        """Return (exitcode, output) of executing cmd in a shell.

        Execute the string 'cmd' in a shell with 'check_output' and
        return a 2-tuple (status, output). The locale encoding is used
        to decode the output and process newlines.

        A trailing newline is stripped from the output.
        The exit status for the command can be interpreted
        according to the rules for the function 'wait'.
        Example:

        >>> import subprocess
        >>> subprocess.getstatusoutput('ls /bin/ls')
        (0, '/bin/ls')
        >>> subprocess.getstatusoutput('cat /bin/junk')
        (1, 'cat: /bin/junk: No such file or directory')
        >>> subprocess.getstatusoutput('/bin/junk')
        (127, 'sh: /bin/junk: not found')
        >>> subprocess.getstatusoutput('/bin/kill $$')
        (-15, '')
        """
        try:
            data = self.check_output(
                cmd, shell=True, universal_newlines=True, stderr=commons.STDOUT
            )
            exitcode = 0
        except subprocess.CalledProcessError as ex:
            data = ex.output
            exitcode = ex.returncode
        #
        data = str(data)
        if data[-1:] == "\n":
            data = data[:-1]
        return exitcode, data

    def getoutput(self, cmd) -> str:
        """Return output (stdout or stderr) of executing cmd in a shell.

        Like getstatusoutput(), except the exit status is ignored
        and the return value is a string containing the command's output.
        Example:

        >>> import subprocess
        >>> subprocess.getoutput('ls /bin/ls')
        '/bin/ls'
        """
        return self.getstatusoutput(cmd)[1]

    # pylint: disable=redefined-builtin
    def run(
        self, *popenargs, input=None, timeout=None, check=False, **kwargs
    ) -> subprocess.CompletedProcess:
        """Run command with arguments and return a CompletedProcess instance.

        The returned instance will have attributes args, returncode,
        stdout and stderr.
        By default, stdout and stderr are not captured,
        and those attributes will be None.
        Pass stdout=PIPE and/or stderr=PIPE in order to capture them.

        If check is True and the exit code was non-zero, it raises a
        CalledProcessError. The CalledProcessError object will have
        the return code in the returncode attribute,
        and output & stderr attributes if those streams
        were captured.

        If timeout is given, and the process takes too long,
        a TimeoutExpired exception will be raised.

        There is an optional argument "input", allowing you to
        pass a string to the subprocess's stdin.  If you use this argument
        you may not also use the Popen constructor's "stdin" argument,
        as it will be used internally.

        The other arguments are the same as for the Popen constructor.

        If universal_newlines=True is passed, the "input" argument
        must be a string and stdout/stderr in the returned object
        will be strings rather than bytes.
        """
        if input is not None:
            if commons.KW_STDIN in kwargs:
                raise ValueError(
                    "stdin and input arguments may not both be used."
                )
            #
            kwargs[commons.KW_STDIN] = commons.PIPE

        with parent.Popen(*popenargs, **kwargs) as process:
            try:
                stdout, stderr = process.communicate(input, timeout=timeout)
            except subprocess.TimeoutExpired as timeout_expired:
                process.kill()
                stdout, stderr = process.communicate()
                raise subprocess.TimeoutExpired(
                    process.args, timeout, output=stdout, stderr=stderr
                ) from timeout_expired
            except Exception as exc:
                logging.error(str(exc))
                process.kill()
                process.wait()
                raise exc
            #
            retcode = process.poll()
        #
        result: subprocess.CompletedProcess = subprocess.CompletedProcess(
            process.args, retcode, stdout, stderr
        )
        self.add(result, **kwargs)
        if check:
            result.check_returncode()
        #
        return result


# vim: fileencoding=utf-8 sw=4 ts=4 sts=4 expandtab autoindent syntax=python:
