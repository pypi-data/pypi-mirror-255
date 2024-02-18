# -*- coding: utf-8 -*-

"""

subprocess_mock.parent

Mocked Subprocesses with accessible I/O streams,
modified from the Python 3.6 subprocess module

Original subprocess module:
    Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>

Mock modifications (c) 2024 by Rainer Schwarzbach

This module allows you connect MockProcess instances, connect to their
input/output/error pipes, and obtain their return codes.

Contents
========
Popen(...) – a class

This file is part of subprocess-mock.

subprocess-mock is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

subprocess-mock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""

import sys

import io
import logging
import multiprocessing
import os
import time
import signal
import subprocess
import builtins
import warnings
import errno
import threading

from multiprocessing.connection import Connection

from time import monotonic as _time
from typing import List

from subprocess_mock import child
from subprocess_mock import commons

if sys.platform == "win32":
    _MSWINDOWS = True

    # pylint: disable=too-few-public-methods
    class STARTUPINFO:
        """Windows: Starupinfo"""

        dwFlags = 0
        hStdInput = None
        hStdOutput = None
        hStdError = None
        wShowWindow = 0

    # pylint: enable=too-few-public-methods
else:
    import select

    _MSWINDOWS = False
    # When select or poll has indicated that the file is writable,
    # we can write up to _PIPE_BUF bytes without risk of blocking.
    # POSIX defines PIPE_BUF as >= 512.
    _PIPE_BUF = getattr(select, "PIPE_BUF", 512)


__all__ = ["Popen"]


# This list holds Popen instances for which the underlying process had not
# exited at the time its __del__ method got called:
# those processes are wait()ed for synchronously from _cleanup()
# when a new Popen object is created, to avoid zombie processes.
_ACTIVE: List["Popen"] = []


def _cleanup():
    for inst in _ACTIVE[:]:
        # pylint: disable=protected-access
        res = inst._internal_poll(_deadstate=sys.maxsize)
        # pylint: enable=protected-access
        if res is not None:
            try:
                _ACTIVE.remove(inst)
            except ValueError:
                # This can happen if two threads create a new Popen instance.
                # It's harmless that it was already removed, so ignore.
                pass
            #
        #
    #


_PLATFORM_DEFAULT_CLOSE_FDS = object()


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument


class Popen:
    """Execute a child program in a new process.

    For a complete description of the arguments see the Python documentation.

    Arguments:
      args: A string, or a sequence of program arguments.

      bufsize: supplied as the buffering argument to the open() function when
          creating the stdin/stdout/stderr pipe file objects

      executable: A replacement program to execute.

      stdin, stdout and stderr: These specify the executed programs' standard
          input, standard output and standard error file handles, respectively.

      preexec_fn: (POSIX only) An object to be called in the child process
          just before the child is executed.

      close_fds: Controls closing or inheriting of file descriptors.

      shell: If true, the command will be executed through the shell.

      cwd: Sets the current directory before the child is executed.

      env: Defines the environment variables for the new process.

      universal_newlines: If true, use universal line endings for file
          objects stdin, stdout and stderr.

      startupinfo and creationflags (Windows only)

      restore_signals (POSIX only)

      start_new_session (POSIX only)

      pass_fds (POSIX only)

      encoding and errors: Text mode encoding and error handling to use for
          file objects stdin, stdout and stderr.

    Attributes:
        stdin, stdout, stderr, pid, returncode
    """

    _child_created = False  # Set here since __del__ checks it

    def __init__(
        self,
        args,
        bufsize=-1,
        executable=None,
        stdin=None,
        stdout=None,
        stderr=None,
        preexec_fn=None,
        close_fds=_PLATFORM_DEFAULT_CLOSE_FDS,
        shell=False,
        cwd=None,
        env=None,
        universal_newlines=False,
        startupinfo=None,
        creationflags=0,
        restore_signals=True,
        start_new_session=False,
        pass_fds=(),
        *,
        encoding=None,
        errors=None,
    ):
        """Create new Popen instance."""
        _cleanup()
        # Held while anything is calling waitpid before returncode has been
        # updated to prevent clobbering returncode if wait() or poll() are
        # called from multiple threads at once.  After acquiring the lock,
        # code must re-check self.returncode to see if another thread just
        # finished a waitpid() call.
        self._waitpid_lock = threading.Lock()
        self._input = None
        self._communication_started = False
        if bufsize is None:
            bufsize = -1  # Restore default
        #
        if not isinstance(bufsize, int):
            raise TypeError("bufsize must be an integer")
        #
        if _MSWINDOWS:
            if preexec_fn is not None:
                raise ValueError(
                    "preexec_fn is not supported on Windows platforms"
                )
            #
            any_stdio_set = (
                stdin is not None or stdout is not None or stderr is not None
            )
            if close_fds is _PLATFORM_DEFAULT_CLOSE_FDS:
                if any_stdio_set:
                    close_fds = False
                else:
                    close_fds = True
                #
            elif close_fds and any_stdio_set:
                raise ValueError(
                    "close_fds is not supported on Windows platforms"
                    " if you redirect stdin/stdout/stderr"
                )
            #
        else:
            # POSIX
            if close_fds is _PLATFORM_DEFAULT_CLOSE_FDS:
                close_fds = True
            #
            if pass_fds and not close_fds:
                warnings.warn("pass_fds overriding close_fds.", RuntimeWarning)
                close_fds = True
            #
            if startupinfo is not None:
                raise ValueError(
                    "startupinfo is only supported on Windows platforms"
                )
            #
            if creationflags != 0:
                raise ValueError(
                    "creationflags is only supported on Windows platforms"
                )
            #
        #
        self.args = args
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.universal_newlines = universal_newlines
        self.encoding = encoding
        self.errors = errors
        # Input and output objects. The general principle is like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # The parent and child objects are file descriptors on all platforms.
        # The parent objects are commons.NO_PIPE (-1) when not using PIPEs.
        # The child objects are -1 when not redirecting.
        (
            p2cread,
            p2cwrite,
            c2pread,
            c2pwrite,
            errread,
            errwrite,
        ) = self._get_handles(stdin, stdout, stderr)
        text_mode = encoding or errors or universal_newlines
        self._closed_child_pipe_fds = False
        try:
            # pylint: disable=consider-using-with
            if p2cwrite != commons.NO_PIPE:
                if isinstance(p2cwrite, Connection):
                    self.stdin = commons.ConnectionWriter(p2cwrite, bufsize)
                else:
                    self.stdin = io.open(p2cwrite, "wb", bufsize)
                #
                if text_mode:
                    self.stdin = io.TextIOWrapper(
                        self.stdin,
                        write_through=True,
                        line_buffering=(bufsize == 1),
                        encoding=encoding,
                        errors=errors,
                    )
            if c2pread != commons.NO_PIPE:
                # self.stdout = io.open(c2pread, "rb", bufsize)
                if isinstance(c2pread, Connection):
                    self.stdout = commons.ConnectionReader(c2pread, bufsize)
                else:
                    self.stdout = io.open(c2pread, "rb", bufsize)
                #
                if text_mode:
                    self.stdout = io.TextIOWrapper(
                        self.stdout, encoding=encoding, errors=errors
                    )
            if errread != commons.NO_PIPE:
                # self.stderr = io.open(errread, "rb", bufsize)
                if isinstance(errread, Connection):
                    self.stderr = commons.ConnectionReader(errread, bufsize)
                else:
                    self.stderr = io.open(errread, "rb", bufsize)
                #
                if text_mode:
                    self.stderr = io.TextIOWrapper(
                        self.stderr, encoding=encoding, errors=errors
                    )

            # pylint: enable=consider-using-with
            self._execute_child(
                args,
                executable,
                pass_fds,
                cwd,
                env,
                shell,
                p2cread,
                p2cwrite,
                c2pread,
                c2pwrite,
                errread,
                errwrite,
            )
        except Exception as exc:
            # Cleanup if the child failed starting.
            for f in filter(None, (self.stdin, self.stdout, self.stderr)):
                try:
                    f.close()
                except OSError:
                    pass  # Ignore EBADF or other errors.

            if not self._closed_child_pipe_fds:
                to_close = []
                if stdin == commons.PIPE:
                    to_close.append(p2cread)
                if stdout == commons.PIPE:
                    to_close.append(c2pwrite)
                if stderr == commons.PIPE:
                    to_close.append(errwrite)
                if hasattr(self, "_devnull"):
                    to_close.append(self._devnull)
                for fd in to_close:
                    if isinstance(fd, Connection):
                        fd.close()
                    else:
                        try:
                            os.close(fd)
                        except OSError:
                            pass

            raise exc

    def _translate_newlines(self, data, encoding, errors):
        data = data.decode(encoding, errors)
        return data.replace("\r\n", "\n").replace("\r", "\n")

    def __enter__(self):
        return self

    # pylint: disable=redefined-builtin
    def __exit__(self, type, value, traceback):
        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()
        try:  # Flushing a BufferedWriter may raise an error
            if self.stdin:
                self.stdin.close()
        finally:
            # Wait for the process to terminate, to avoid zombies.
            self.wait()

    def __del__(self, _maxsize=sys.maxsize, _warn=warnings.warn):
        if not self._child_created:
            # We didn't get to successfully create a child process.
            return
        if self.returncode is None:
            # Not reading subprocess exit status creates a zombi process which
            # is only destroyed at the parent python process exit
            _warn(
                f"subprocess {self.pid} is still running",
                ResourceWarning,
                source=self,
            )
        # In case the child hasn't been waited on, check if it's done.
        self._internal_poll(_deadstate=_maxsize)
        if self.returncode is None and _ACTIVE is not None:
            # Child is still running, keep us alive until we can wait on it.
            _ACTIVE.append(self)

    def _get_devnull(self):
        if not hasattr(self, "_devnull"):
            self._devnull = os.open(os.devnull, os.O_RDWR)
        #
        return self._devnull

    def _stdin_write(self, input):
        if input:
            try:
                self.stdin.write(input)
            except BrokenPipeError:
                pass  # communicate() must ignore broken pipe errors.
            except OSError as exc:
                if exc.errno == errno.EINVAL:
                    # bpo-19612, bpo-30418: On Windows, stdin.write() fails
                    # with EINVAL if the child process exited or if the child
                    # process is still running but closed the pipe.
                    pass
                else:
                    raise

        try:
            self.stdin.close()
        except BrokenPipeError:
            pass  # communicate() must ignore broken pipe errors.
        except OSError as exc:
            if exc.errno == errno.EINVAL:
                pass
            else:
                raise

    def communicate(self, input=None, timeout=None):
        """Interact with process: Send data to stdin.  Read data from
        stdout and stderr, until end-of-file is reached.  Wait for
        process to terminate.

        The optional "input" argument should be data to be sent to the
        child process (if self.universal_newlines is True, this should
        be a string; if it is False, "input" should be bytes), or
        None, if no data should be sent to the child.

        communicate() returns a tuple (stdout, stderr).  These will be
        bytes or, if self.universal_newlines was True, a string.
        """

        if self._communication_started and input:
            raise ValueError("Cannot send input after starting communication")
        #
        if timeout is not None:
            endtime = _time() + timeout
        else:
            endtime = None
        #
        try:
            stdout, stderr = self._communicate(input, endtime, timeout)
        finally:
            self._communication_started = True
        #
        self.wait(timeout=self._remaining_time(endtime))
        return (stdout, stderr)

    def poll(self):
        """Check if child process has terminated. Set and return returncode
        attribute."""
        return self._internal_poll()

    def _remaining_time(self, endtime):
        """Convenience for _communicate when computing timeouts."""
        if endtime is None:
            return None
        #
        return endtime - _time()

    def _check_timeout(self, endtime, orig_timeout):
        """Convenience for checking if a timeout has expired."""
        if endtime is None:
            return
        #
        if _time() > endtime:
            raise subprocess.TimeoutExpired(self.args, orig_timeout)
        #

    #
    # POSIX methods
    #

    def _get_handles(self, stdin, stdout, stderr):
        """Construct and return tuple with IO objects:
        p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
        """
        p2cread, p2cwrite = commons.NO_PIPE, commons.NO_PIPE
        c2pread, c2pwrite = commons.NO_PIPE, commons.NO_PIPE
        errread, errwrite = commons.NO_PIPE, commons.NO_PIPE

        if stdin is None:
            pass
        elif stdin == commons.PIPE:
            p2cread, p2cwrite = multiprocessing.Pipe(duplex=False)
        elif stdin == commons.DEVNULL:
            p2cread = self._get_devnull()
        elif isinstance(stdin, int):
            p2cread = stdin
        else:
            # Assuming file-like object
            p2cread = stdin.fileno()

        if stdout is None:
            pass
        elif stdout == commons.PIPE:
            c2pread, c2pwrite = multiprocessing.Pipe(duplex=False)
        elif stdout == commons.DEVNULL:
            c2pwrite = self._get_devnull()
        elif isinstance(stdout, int):
            c2pwrite = stdout
        else:
            # Assuming file-like object
            c2pwrite = stdout.fileno()

        if stderr is None:
            pass
        elif stderr == commons.PIPE:
            errread, errwrite = multiprocessing.Pipe(duplex=False)
        elif stderr == commons.STDOUT:
            if c2pwrite != commons.NO_PIPE:
                errwrite = c2pwrite
            else:  # child's stdout is not set, use parent's stdout
                errwrite = sys.__stdout__.fileno()
        elif stderr == commons.DEVNULL:
            errwrite = self._get_devnull()
        elif isinstance(stderr, int):
            errwrite = stderr
        else:
            # Assuming file-like object
            errwrite = stderr.fileno()

        return (p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite)

    def _execute_child(
        self,
        args,
        executable,
        pass_fds,
        cwd,
        env,
        shell,
        p2cread,
        p2cwrite,
        c2pread,
        c2pwrite,
        errread,
        errwrite,
    ):
        """Execute program (POSIX version)"""

        if isinstance(args, (str, bytes)):
            args = [args]
        else:
            args = list(args)

        if shell:
            args = ["/bin/sh", "-c"] + args
            if executable:
                args[0] = executable

        if executable is None:
            executable = args[0]
        # orig_executable = executable

        # For transferring possible exec failure from child to parent.
        # Data format: "exception name:description"
        # Pickle is not used; it is complex and involves memory allocation.
        errpipe_read, errpipe_write = multiprocessing.Pipe(duplex=False)
        try:
            # We must avoid complex work that could involve
            # malloc or free in the child process to avoid
            # potential deadlocks, thus we do all this here.
            # and pass it to fork_exec()
            if env is not None:
                env_list = []
                for k, v in env.items():
                    k = os.fsencode(k)
                    if b"=" in k:
                        raise ValueError("illegal environment variable name")
                    #
                    env_list.append(k + b"=" + os.fsencode(v))
                #
            else:
                env_list = None  # Use execv instead of execve.
            #
            # fds_to_keep = set(pass_fds)
            # fds_to_keep.add(errpipe_write)
            logging.debug("[parent] Starting %r subprocess …", args)
            self.mocked_child_process = multiprocessing.Process(
                target=child.run_process,
                kwargs={
                    commons.KW_STDIN: p2cread,
                    commons.KW_STDOUT: c2pwrite,
                    commons.KW_STDERR: errwrite,
                    "error_channel": errpipe_write,
                },
            )
            logging.debug("[parent] … process created")
            self.mocked_child_process.start()
            self.pid = self.mocked_child_process.pid
            self._child_created = True
            #
            # close child pipelines
            # self._devnull is not always defined.
            devnull_fd = getattr(self, "_devnull", None)
            if (
                p2cread != -1
                and p2cwrite != -1
                and p2cread != devnull_fd
                and isinstance(p2cread, int)
            ):
                os.close(p2cread)
            if (
                c2pwrite != -1
                and c2pread != -1
                and c2pwrite != devnull_fd
                and isinstance(c2pwrite, int)
            ):
                os.close(c2pwrite)
            if (
                errwrite != -1
                and errread != -1
                and errwrite != devnull_fd
                and isinstance(errwrite, int)
            ):
                os.close(errwrite)
            if devnull_fd is not None:
                os.close(devnull_fd)
            # Prevent a double close of these fds from __init__ on error.
            self._closed_child_pipe_fds = True

            # Wait for exec to fail or succeed; possibly raising an
            # exception (limited in size)
            errpipe_data = bytearray()
            while not errpipe_read.poll():
                logging.debug(
                    "[parent] … waiting for process %s startup", self.pid
                )
                time.sleep(0.5)
            #
            try:
                errpipe_data.extend(errpipe_read.recv_bytes())
            except EOFError:
                pass
            #
        finally:
            # be sure the FD is closed no matter what
            errpipe_read.close()
        #
        if errpipe_data:
            try:
                pid, sts = os.waitpid(self.pid, 0)
                if pid == self.pid:
                    self._handle_exitstatus(sts)
                else:
                    self.returncode = sys.maxsize
                #
            except ChildProcessError:
                pass
            #
            try:
                exception_name, err_msg = errpipe_data.split(b":")
                # The encoding here should match the encoding
                # written in by the subprocess implementations
                # like _posixsubprocess
                err_msg = err_msg.decode()
            except ValueError:
                exception_name = b"SubprocessError"
                err_msg = (
                    f"Bad exception data from child: {bytes(errpipe_data)!r}"
                )
            #
            child_exception_type = getattr(
                builtins,
                exception_name.decode("ascii"),
                subprocess.SubprocessError,
            )
            raise child_exception_type(err_msg)
        #

    # pylint: disable=invalid-name
    def _handle_exitstatus(
        self,
        sts,
        _WIFSIGNALED=os.WIFSIGNALED,
        _WTERMSIG=os.WTERMSIG,
        _WIFEXITED=os.WIFEXITED,
        _WEXITSTATUS=os.WEXITSTATUS,
        _WIFSTOPPED=os.WIFSTOPPED,
        _WSTOPSIG=os.WSTOPSIG,
    ):
        """All callers to this function MUST hold self._waitpid_lock."""
        # This method is called (indirectly) by __del__, so it cannot
        # refer to anything outside of its local scope.
        if _WIFSIGNALED(sts):
            self.returncode = -_WTERMSIG(sts)
        elif _WIFEXITED(sts):
            self.returncode = _WEXITSTATUS(sts)
        elif _WIFSTOPPED(sts):
            self.returncode = -_WSTOPSIG(sts)
        else:
            # Should never happen
            raise subprocess.SubprocessError("Unknown child exit status!")
        #

    def _internal_poll(
        self,
        _deadstate=None,
        _waitpid=os.waitpid,
        _WNOHANG=os.WNOHANG,
        _ECHILD=errno.ECHILD,
    ):
        """Check if child process has terminated.  Returns returncode
        attribute.

        This method is called by __del__, so it cannot reference anything
        outside of the local scope (nor can any methods it calls).

        """
        if self.returncode is None:
            # pylint: disable=consider-using-with
            if not self._waitpid_lock.acquire(False):
                # Something else is busy calling waitpid.  Don't allow two
                # at once.  We know nothing yet.
                return None
            try:
                if self.returncode is not None:
                    return self.returncode  # Another thread waited.
                pid, sts = os.waitpid(self.pid, _WNOHANG)
                if pid == self.pid:
                    self._handle_exitstatus(sts)
            except OSError as e:
                if _deadstate is not None:
                    self.returncode = _deadstate
                elif e.errno == _ECHILD:
                    # This happens if SIGCLD is set to be ignored or
                    # waiting for child processes has otherwise been
                    # disabled for our process.  This child is dead, we
                    # can't get the status.
                    # http://bugs.python.org/issue15756
                    self.returncode = 0
            finally:
                self._waitpid_lock.release()
        return self.returncode

    # pylint: enable=invalid-name
    def _try_wait(self, wait_flags):
        """All callers to this function MUST hold self._waitpid_lock."""
        try:
            (pid, sts) = os.waitpid(self.pid, wait_flags)
        except ChildProcessError:
            # This happens if SIGCLD is set to be ignored or waiting
            # for child processes has otherwise been disabled for our
            # process.  This child is dead, we can't get the status.
            pid = self.pid
            sts = 0
        return (pid, sts)

    def wait(self, timeout=None, endtime=None):
        """Wait for child process to terminate.  Returns returncode
        attribute."""
        if self.returncode is not None:
            return self.returncode

        if endtime is not None:
            warnings.warn(
                "'endtime' argument is deprecated; use 'timeout'.",
                DeprecationWarning,
                stacklevel=2,
            )
        if endtime is not None or timeout is not None:
            if endtime is None:
                endtime = _time() + timeout
            elif timeout is None:
                timeout = self._remaining_time(endtime)

        if endtime is not None:
            # Enter a busy loop if we have a timeout.  This busy loop was
            # cribbed from Lib/threading.py in Thread.wait() at r71065.
            delay = 0.0005  # 500 us -> initial delay of 1 ms
            while True:
                # pylint: disable=consider-using-with
                if self._waitpid_lock.acquire(False):
                    try:
                        if self.returncode is not None:
                            break  # Another thread waited.
                        (pid, sts) = self._try_wait(os.WNOHANG)
                        assert pid in {self.pid, 0}
                        if pid == self.pid:
                            self._handle_exitstatus(sts)
                            break
                    finally:
                        self._waitpid_lock.release()
                remaining = self._remaining_time(endtime)
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(self.args, timeout)
                delay = min(delay * 2, remaining, 0.05)
                time.sleep(delay)
        else:
            while self.returncode is None:
                with self._waitpid_lock:
                    if self.returncode is not None:
                        break  # Another thread waited.
                    (pid, sts) = self._try_wait(0)
                    # Check the pid and loop as waitpid has been known to
                    # return 0 even without WNOHANG in odd situations.
                    # http://bugs.python.org/issue14396.
                    if pid == self.pid:
                        self._handle_exitstatus(sts)
        return self.returncode

    def _communicate(self, input, endtime, orig_timeout):
        """Communicate and return the (stdout, stderr) tuple"""
        if self.stdin and not self._communication_started:
            # Flush stdio buffer.  This might block, if the user has
            # been writing to .stdin in an uncontrolled fashion.
            try:
                self.stdin.flush()
            except BrokenPipeError:
                pass  # communicate() must ignore BrokenPipeError.
            #
            if not input:
                try:
                    self.stdin.close()
                except BrokenPipeError:
                    pass  # communicate() must ignore BrokenPipeError.
                #
            #
        #
        stdout = None
        stderr = None
        # Only create this mapping if we haven't already.
        if not self._communication_started:
            self._fileobj2output = {}
            self._pipe_broken = {}
            if self.stdout:
                self._fileobj2output[self.stdout] = []
                self._pipe_broken[self.stdout] = False
            #
            if self.stderr:
                self._fileobj2output[self.stderr] = []
                self._pipe_broken[self.stderr] = False
            #
        #
        if self.stdout:
            stdout = self._fileobj2output[self.stdout]
        #
        if self.stderr:
            stderr = self._fileobj2output[self.stderr]
        #
        self._save_input(input)
        if self._input:
            input_view = memoryview(self._input)
            while self._input_offset < len(self._input):
                mv_start = self._input_offset
                mv_end = self._input_offset + _PIPE_BUF
                chunk = input_view[mv_start:mv_end]
                try:
                    logging.debug(
                        "[parent] writing chunk to child: %r", bytes(chunk)
                    )
                    self._input_offset += self.stdin.write(chunk)
                except BrokenPipeError:
                    self.stdin.close()
                    break
                else:
                    logging.debug("[parent] … wrote to child")
                    if self._input_offset >= len(self._input):
                        self.stdin.close()
                    #
                #
            #
        #
        while True:
            time.sleep(0.1)
            for fileobj in (self.stdout, self.stderr):
                if not fileobj:
                    continue
                #
                if self._pipe_broken.get(fileobj, True):
                    continue
                #
                try:
                    data = fileobj.read()
                except BrokenPipeError:
                    logging.warning("[parent] Pipe broken: %r", fileobj)
                    self._pipe_broken[fileobj] = True
                else:
                    if data:
                        logging.debug(
                            "[parent] Got data from %r: %r", fileobj, data
                        )
                        self._fileobj2output[fileobj].append(data)
                    #
                #
            #
            if all(probe for probe in self._pipe_broken.values()):
                break
            #
            if not self.mocked_child_process.is_alive():
                break
            #
        #
        self.wait(timeout=self._remaining_time(endtime))
        # All data exchanged.  Translate lists into strings.
        if stdout is not None:
            stdout = b"".join(stdout)
        #
        if stderr is not None:
            stderr = b"".join(stderr)
        #
        # Translate newlines, if requested.
        # This also turns bytes into strings.
        if self.encoding or self.errors or self.universal_newlines:
            if stdout is not None:
                stdout = self._translate_newlines(
                    stdout, self.stdout.encoding, self.stdout.errors
                )
            #
            if stderr is not None:
                stderr = self._translate_newlines(
                    stderr, self.stderr.encoding, self.stderr.errors
                )
            #
        #
        return (stdout, stderr)

    def _save_input(self, input):
        """This method is called from the _communicate_with_*() methods
        so that if we time out while communicating, we can continue
        sending input if we retry.
        """
        if self.stdin and self._input is None:
            self._input_offset = 0
            self._input = input
            if input is not None and (
                self.encoding or self.errors or self.universal_newlines
            ):
                self._input = self._input.encode(
                    self.stdin.encoding, self.stdin.errors
                )
            #
        #

    def send_signal(self, sig):
        """Send a signal to the process."""
        # Skip signalling a process that we know has already died.
        if self.returncode is None:
            os.kill(self.pid, sig)

    def terminate(self):
        """Terminate the process with SIGTERM"""
        self.mocked_child_process.terminate()

    def kill(self):
        """Kill the process with SIGKILL"""
        self.send_signal(signal.SIGKILL)


# vim: fileencoding=utf-8 sw=4 ts=4 sts=4 expandtab autoindent syntax=python:
