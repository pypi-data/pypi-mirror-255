# -*- coding: utf-8 -*-

"""

subprocess_mock.commons

subprocess-mock common definitions

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
import subprocess

from multiprocessing import Lock
from multiprocessing.connection import Connection


# Magic numbers
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
DEVNULL = subprocess.DEVNULL
NO_PIPE = -1  # to be used instead of literal -1

KW_ARGS = "args"
KW_RETURNCODE = "returncode"
KW_STDIN = "stdin"
KW_STDERR = "stderr"
KW_STDOUT = "stdout"

RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


# pylint: disable=too-many-instance-attributes


class ConnectionWrapper:

    """ConnectionWrapper(connection[, buffer_size])

    A wrapper for file-like access to a
    multiprocessing.connection.Connection instance,
    providing file-read access.

    If buffer_size is omitted, io.DEFAULT_BUFFER_SIZE is used.
    """

    readable = False
    writable = False
    seekable = False

    def __init__(
        self,
        connection: Connection,
        buffer_size: int = io.DEFAULT_BUFFER_SIZE,
    ) -> None:
        """Create a new stream using the given Connection instance."""
        if self.readable and not connection.readable:
            raise OSError('"connection" argument must be readable.')
        #
        if self.writable and not connection.writable:
            raise OSError('"connection" argument must be writable.')
        #
        if buffer_size == -1:
            buffer_size = 0
        #
        if buffer_size < 0:
            raise ValueError(f"invalid buffer size: {buffer_size}")
        #
        super().__init__()
        self.__connection = connection
        self._raw = bytearray()
        self.buffer_size = buffer_size
        self._closed = False

    @property
    def raw(self) -> bytearray:
        """Property: raw buffer"""
        return self._raw

    @property
    def connection(self) -> Connection:
        """Property: connection"""
        return self.__connection

    @property
    def closed(self) -> bool:
        """Property: connection closed?"""
        return self._closed

    def close(self) -> None:
        """Close the connection"""
        if not self.closed:
            self.__connection.close()
            self._closed = True
        #

    def seek(self, pos, whence=0):
        """Set the position in the stream. Not supported."""
        raise ValueError("This stream is not seekable.")

    # pylint: disable=unused-argument
    def write(self, data: bytes) -> int:
        """Write data to the stream."""
        if not self.writable:
            raise ValueError("This stream is not writable.")
        #
        return 0

    def flush(self) -> None:
        """Flush the stream."""
        if not self.writable:
            raise ValueError(
                "This stream is not writable and cannot be flushed."
            )
        #


class ConnectionReader(ConnectionWrapper):

    """ConnectionReader(connection[, buffer_size])

    A wrapper for read access to a multiprocessing.connection.Connection
    instance, providing non-blocking, file-like read access.

    Uses an internal second-level read buffer

    If buffer_size is omitted, io.DEFAULT_BUFFER_SIZE is used.
    """

    readable = True

    def __init__(
        self,
        connection: Connection,
        buffer_size: int = io.DEFAULT_BUFFER_SIZE,
    ) -> None:
        """Create a new buffered reader using the given
        readable Connection instance.
        """
        super().__init__(connection, buffer_size=buffer_size)
        self._eof = False
        self._total_read_bytes = 0
        self._read_buf = bytearray()
        self._read_pos = 0
        self._read_lock = Lock()

    def _reset_read_buf(self):
        """Reset the second-level read buffer"""
        self._read_buf.clear()
        self._read_pos = 0

    def read(self, size=None, blocking=False):
        """Read size bytes.

        Returns exactly size bytes of data unless the underlying raw IO
        stream reaches EOF or if the call would block in non-blocking
        mode. If size is negative, read until EOF or until read() would
        block.
        """
        if size is not None and size < -1:
            raise ValueError("invalid number of bytes to read")
        with self._read_lock:
            return self._read_unlocked(size, blocking=blocking)

    def _update_raw_unlocked(self):
        """Update the internal bytearray"""
        try:
            read_data = self.connection.recv_bytes()
        except EOFError:
            self._eof = True
        else:
            self.raw.extend(read_data)
        #

    def _update_raw_unlocked_noblock(self):
        """Update the internal bytearray"""
        if self._eof:
            return
        #
        while self.connection.poll():
            self._update_raw_unlocked()
            if self._eof:
                break
            #
        #

    def _update_read_buffer_unlocked(self, n=None):
        """Update the read buffer from the internal byte array,
        remove the number of bytes from the internal byte array's
        start, then return the number of bytes transferred
        """
        if n is None or n >= len(self.raw):
            self._read_buf.extend(self.raw)
            n_read = len(self.raw)
            self.raw.clear()
            return n_read
        #
        if n < 1:
            raise ValueError("n must be at least 1")
        #
        self._read_buf.extend(self.raw[:n])
        del self.raw[:n]
        return n

    def _read_unlocked(self, n=None, blocking=False):
        """Read data from the internal buffer"""
        nodata_val = b""
        if blocking:
            self._update_raw_unlocked()
        else:
            self._update_raw_unlocked_noblock()
        #
        self._update_read_buffer_unlocked()
        if self._eof and not self._read_buf:
            return nodata_val
        #
        buf = self._read_buf[:]
        pos = self._read_pos

        # Special case for when the number of bytes to read is unspecified.
        if n is None or n == -1:
            self._reset_read_buf()
            out = buf[pos:]  # Strip the consumed bytes.
            self._total_read_bytes += len(out)
            return bytes(out)

        # The number of bytes to read is specified, return at most n bytes.
        avail = len(buf) - pos  # Length of the available buffered data.
        if n <= avail:
            # Fast path: the data to read is fully buffered.
            end_pos = pos + n
            self._read_pos = end_pos
            self._total_read_bytes += n
            return bytes(buf[pos:end_pos])
        # Slow path: read from the stream until enough bytes are read,
        # or until an EOF occurs or until read() would block.
        while avail < n:
            self._update_raw_unlocked_noblock()
            avail += self._update_read_buffer_unlocked()
            if self._eof:
                break
            #
        # n is more than avail only when an EOF occurred or when
        # read() would have blocked.
        n_read = min(n, avail)
        end_pos = pos + n_read
        buf = self._read_buf[:]
        self._read_buf = buf[n:]  # Save the extra data in the buffer.
        self._read_pos = 0
        self._total_read_bytes += n_read
        return bytes(buf[pos:end_pos])

    def peek(self, size=0):
        """Returns buffered bytes without advancing the position.

        The argument indicates a desired minimal number of bytes.
        We never return more than self.buffer_size.
        """
        with self._read_lock:
            return self._peek_unlocked(size)
        #

    def _peek_unlocked(self, n=0):
        """Return at most n bytes from the read buffer without consuming any"""
        self._update_raw_unlocked_noblock()
        self._update_read_buffer_unlocked()
        if self.buffer_size:
            want = min(n, self.buffer_size)
        else:
            want = n
        #
        have = len(self._read_buf) - self._read_pos
        start_pos = self._read_pos
        end_pos = start_pos + min(want, have)
        return self._read_buf[start_pos:end_pos]

    def read1(self, size):
        """Reads up to size bytes, with at most one read() system call."""
        # Returns up to size bytes.  If at least one byte is buffered, we
        # only return buffered bytes.  Otherwise, we do one raw read.
        if size < 0:
            raise ValueError("number of bytes to read must be positive")
        if size == 0:
            return b""
        with self._read_lock:
            self._peek_unlocked(1)
            return self._read_unlocked(
                min(size, len(self._read_buf) - self._read_pos)
            )
        #

    # Implementing readinto() and readinto1() is not strictly necessary (we
    # could rely on the base class that provides an implementation in terms of
    # read() and read1()). We do it anyway to keep the _pyio implementation
    # similar to the io implementation (which implements the methods for
    # performance reasons).
    def _readinto(self, buf, read1):
        """Read data into *buf* with at most one system call."""

        # Need to create a memoryview object of type 'b', otherwise
        # we may not be able to assign bytes to it, and slicing it
        # would create a new object.
        if isinstance(buf, memoryview):
            write_buf = buf
        else:
            write_buf = memoryview(buf)
        #
        del buf
        if write_buf.nbytes == 0:
            return 0
        write_buf = write_buf.cast("B")

        written = 0
        with self._read_lock:
            while written < len(write_buf):
                self._update_raw_unlocked_noblock()
                self._update_read_buffer_unlocked()

                # First try to read from internal buffer
                avail = min(
                    len(self._read_buf) - self._read_pos, len(write_buf)
                )
                if avail:
                    write_end = written + avail
                    read_start = self._read_pos
                    read_end = read_start + avail
                    write_buf[written:write_end] = self._read_buf[
                        read_start:read_end
                    ]
                    self._read_pos = read_end
                    written = write_end
                    self._total_read_bytes += avail
                    if written == len(write_buf):
                        break

                # Otherwise refill internal buffer - unless we're
                # in read1 mode and already got some data
                elif not (read1 and written):
                    if not self._peek_unlocked(1):
                        break  # eof

                # In readinto1 mode, return as soon as we have some data
                if read1 and written:
                    break

        return written

    def tell(self):
        """Tell the current position in the stream"""
        return self._total_read_bytes


class ConnectionWriter(ConnectionWrapper):

    """ConnectionWriter(connection[, buffer_size])

    A wrapper for write access to a multiprocessing.connection.Connection
    instance, file-like access.

    If buffer_size is omitted, io.DEFAULT_BUFFER_SIZE is used.
    """

    writable = True

    def __init__(
        self,
        connection: Connection,
        buffer_size: int = io.DEFAULT_BUFFER_SIZE,
    ) -> None:
        """Create a new buffered reader using the given
        readable Connection instance.
        """
        super().__init__(connection, buffer_size=buffer_size)
        self._write_lock = Lock()

    def write(self, data: bytes) -> int:
        """Write data to the connection"""
        with self._write_lock:
            written_bytes = self._write_unlocked(data)
        #
        return written_bytes

    def _write_unlocked(self, data: bytes) -> int:
        """Write data to the connection in chunks of self.buffer_size"""
        self.raw.extend(data)
        if self.buffer_size == 0:
            out_bytes = bytes(self.raw)
            self.raw.clear()
            self.connection.send_bytes(out_bytes)
            return len(out_bytes)
        #
        out = bytearray()
        raw_size = len(self.raw)
        start_pos = 0
        end_pos = self.buffer_size
        while end_pos <= raw_size:
            out.extend(self.raw[start_pos:end_pos])
            start_pos = end_pos
            end_pos += self.buffer_size
        #
        del self.raw[:start_pos]
        self.connection.send_bytes(bytes(out))
        return len(out)

    def flush(self) -> None:
        """Flush the internal buffer"""
        with self._write_lock:
            if self.raw:
                self.connection.send_bytes(bytes(self.raw))
                self.raw.clear()
            #
        #

    def close(self) -> None:
        """Flush the buffer before closing"""
        self.flush()
        super().close()


# vim: fileencoding=utf-8 sw=4 ts=4 sts=4 expandtab autoindent syntax=python:
