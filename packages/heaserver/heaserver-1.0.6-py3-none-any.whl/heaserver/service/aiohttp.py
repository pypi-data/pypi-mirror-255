"""
Utility classes and functions for working with aiohttp.
"""
import asyncio
from contextlib import AbstractContextManager
from multiprocessing.connection import Connection
from io import BytesIO
from aiohttp.streams import StreamReader
from aiohttp.web import StreamResponse, Request
from aiohttp.client import ClientSession
from typing import Protocol, AsyncIterator, BinaryIO
from heaobject.root import json_dumps
from .appproperty import HEA_COMPONENT
from contextlib import asynccontextmanager
import logging
import os
import time

from yarl import URL


CHUNK_SIZE = 16 * 1024


@asynccontextmanager
async def client_session(*args, **kwargs) -> AsyncIterator[ClientSession]:
    """
    Gets a new aiohttp ClientSession. The session's json_serialize parameter is set to heaobject.root.json_dumps,
    which unlike Python's native json serialization supports serializing timestamps. It supports any arguments that
    ClientSession's constructor supports.
    """
    session = ClientSession(json_serialize=json_dumps, *args, **kwargs)
    try:
        yield session
    finally:
        await session.close()


class ConnectionFileLikeObjectWrapper(AbstractContextManager):
    """
    Wraps a multiprocessing.connection.Connection object and provides file-like object methods.

    This class is a context manager, so it can be used in with statements.
    """

    def __init__(self, conn: Connection):
        """
        Creates a new ConnectionFileLikeObjectWrapper object, passing in the connection to wrap.

        :param conn: a multiprocessing.connection.Connection object (required).
        """
        if conn is None:
            raise ValueError('conn cannot be None')
        self.__conn = conn
        self.__buffer = BytesIO()

    def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        if len(b := self.__buffer.read(n)) > 0:
            return b
        try:
            result: bytes = self.__conn.recv_bytes()
            if -1 < n < len(result):
                pos = self.__buffer.tell()
                self.__buffer.write(result[n:])
                self.__buffer.seek(pos)
                return result[:n]
            else:
                return result
        except EOFError:
            return b''

    def write(self, b):
        """
        Sends some bytes to the connection.

        :param b: some bytes (required).
        """
        self.__conn.send_bytes(b)

    def fileno(self):
        """
        Returns the integer file descriptor that is used by the connection.

        :return: the integer file descriptor.
        """
        return self.__conn.fileno()

    def close(self):
        """
        Closes the connection and any other resources associated with this object.
        """
        try:
            self.__buffer.close()
            self.__conn.close()
            self.__conn = None
        finally:
            if self.__conn is not None:
                try:
                    self.conn.close()
                except OSError:
                    pass

    def __exit__(self, *exc_details):
        self.close()


class SupportsAsyncRead(Protocol):
    """
    Protocol with an async read() method and a close() method.
    """

    async def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        pass

    def close(self):
        """
        Closes any resources associated with this object.
        """
        pass


class AsyncReader:
    """
    Wraps a bytes object in a simple reader with an asynchronous read method and a close method.
    """

    def __init__(self, b: bytes):
        """
        Creates a new AsyncReader, passing in a bytes object.

        :param b: bytes (required).
        """
        self.__b = BytesIO(b)

    async def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        return self.__b.read(n)

    def close(self):
        """
        Closes any resources associated with this object.
        """
        self.__b.close()


class StreamReaderWrapper:
    """
    Wraps an aiohttp StreamReader in an asyncio StreamReader-like object with a read() method and a no-op close()
    method.
    """

    def __init__(self, reader: StreamReader):
        if reader is None:
            raise ValueError('reader cannot be None')
        self.__reader = reader

    async def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        return await self.__reader.read(n)

    def close(self):
        pass


class StreamResponseFileLikeWrapper:
    """
    Wraps an aiohttp StreamResponse in a file-like object wrapper. The write() method must be called in a separate
    thread.
    """

    def __init__(self, resp: StreamResponse, loop: asyncio.AbstractEventLoop = None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_running_loop()
        self.resp = resp
        self.__successful = False
        self.__error_msg = None
        self.__logger = logging.getLogger(__name__)
        self.__queue = asyncio.Queue(maxsize=1024)
        self.__task = self.loop.create_task(self.__pump_bytes_into_fd())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def write(self, data: bytes) -> int:
        """
        Writes to the StreamResponse and returns how many bytes were written.

        :param data: the bytes to write (required).
        :return: the number of bytes written.
        """
        self.__logger.debug('Writing %s', data)
        while True:
            try:
                self.__queue.put_nowait(data)
                break
            except asyncio.QueueFull:
                time.sleep(0.1)
        return len(data)

    def flush(self):
        """
        Flush the write buffers of the stream if applicable.
        """
        pass

    async def close(self):
        """
        Cleans up all resources in this file-like object.
        """
        self.__logger.debug('Closing')
        await self.__queue.put(b'')
        await self.__task
        self.__logger.debug('Task done')
        if not self.__successful:
            raise IOError(f'Failed writing data to the response: {self.__error_msg}')
        self.__logger.debug('Closed')

    async def __pump_bytes_into_fd(self):
        try:
            self.__logger.debug('About to write')
            while True:
                try:
                    while (chunk := await self.__queue.get()) != b'':
                        self.__logger.debug('Read %d bytes from download', len(chunk))
                        await self.resp.write(chunk)
                        self.__queue.task_done()
                        self.__logger.debug('Wrote %d bytes to stream writer', len(chunk))
                    self.__queue.task_done()
                    break
                except asyncio.CancelledError as e:
                    # On Windows, closing the write side of the pipe triggers a CancelledError, which we need to deal
                    # with here.
                    self.__logger.debug(f'Cancelled but continuing: {e}')
                    continue
            self.__successful = True
            self.__logger.debug('Done reading file')
        except OSError as e:
            self.__logger.exception('Failed to read file')
            self.__error_msg = str(e)
            raise e
        self.__logger.debug('Exiting task')


class RequestFileLikeWrapper:
    """
    Wraps an aiohttp request's content in a file-like object with read() and close() functions. Before doing any
    reading, call the initialize() method. The read() method must be called in a separate thread.
    """

    def __init__(self, request: Request, loop: asyncio.AbstractEventLoop = None):
        """
        Creates the file-like object wrapper.

        :param request: the aiohttp request (required).
        :param loop: the current event loop. If None, it will use asyncio.get_running_loop().
        """
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_running_loop()
        self.request = request
        self.__pump_task: asyncio.Task | None = None
        self.__reader: BinaryIO | None = None
        self.__writer: BinaryIO | None = None

    def initialize(self):
        """
        Creates resources needed for reading.
        """
        read_fd, write_fd = os.pipe()
        self.__pump_task = self.loop.create_task(self.__pump_bytes_into_fd())
        self.__reader = os.fdopen(read_fd, 'rb')
        self.__writer = os.fdopen(write_fd, 'wb')

    def read(self, n=-1, /) -> bytes:
        """
        Reads some bytes.

        :param n: the number of bytes to read (or -1 for everything).
        :return: the bytes that were read.
        """
        logger = logging.getLogger(__name__)
        logger.debug('Reading %s bytes', n)
        output = self.__reader.read(n)
        logger.debug('Read %s bytes', len(output))
        return output

    def close(self):
        """
        Cleans up all resources in this file-like object.
        """
        logger = logging.getLogger(__name__)
        logger.debug('Closing')
        try:
            if self.__writer is not None:
                self.__writer.close()
                self.__writer = None
            if self.__reader is not None:
                self.__reader.close()
                self.__reader = None
            while self.__pump_task is not None and not self.__pump_task.done():
                time.sleep(0.1)
            self.__pump_task = None
        except Exception as e:
            logger.exception('Failed to close pipe')
            if self.__reader is not None:
                try:
                    self.__reader.close()
                    self.__reader = None
                except:
                    pass
            try:
                while self.__pump_task is not None and not self.__pump_task.done():
                    time.sleep(0.1)
                self.__pump_task = None
            except:
                pass
            raise e

    async def __pump_bytes_into_fd(self):
        logger = logging.getLogger(__name__)
        writer_closed = False
        content_type = self.request.headers.get('Content-Type', '')
        try:
            if content_type.startswith('multipart/form-data'):
                logger.debug(f'Is multipart')
                mp_reader = await self.request.multipart()
                while True:
                    part = await mp_reader.next()
                    if part is None:
                        break
                    logger.debug("the part's headers %s" % part.headers)
                    while True:
                        chunk = await part.read_chunk(CHUNK_SIZE)
                        if not chunk or chunk == b'':
                            break
                        logger.debug('Read %d bytes from upload', len(chunk))
                        bytes_written = await self.loop.run_in_executor(None, self.__writer.write, chunk)
                        logger.debug('Wrote %d bytes to pipe', bytes_written)
            else:
                while not self.request.content.at_eof():
                    chunk = await self.request.content.read(CHUNK_SIZE)
                    logger.debug('Read %d bytes from upload', len(chunk))
                    bytes_written = await self.loop.run_in_executor(None, self.__writer.write, chunk)
                    logger.debug('Wrote %d bytes to pipe', bytes_written)
            self.__writer.close()
            writer_closed = True
            logger.debug('Done reading file')
        except Exception as e:
            logger.exception('Failed to read file')
            if not writer_closed:
                try:
                    self.__writer.close()
                except:
                    pass
                writer_closed = False
                raise e

def absolute_url_minus_base(request: Request, url: URL | str | None = None) -> str:
    """
    Removes the current service's base URL from the beginning of the provided URL. If no URL is provided, the request
    URL is used. If the provided URL is not prefixed with the service's base URL, the URL is returned unaltered.

    :param request: the HTTP request (required).
    :param url: optional URL.
    :return: the resulting URL.
    """
    if url is None:
        url_ = str(request.url)
    else:
        url_ = str(url)
    base_url = request.app[HEA_COMPONENT]
    if not url_.startswith(base_url):
        return url
    else:
        return url_.removeprefix(base_url).lstrip('/')
