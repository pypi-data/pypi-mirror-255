from __future__ import annotations

import gzip
import os
import shutil
import zlib
from contextlib import contextmanager
from typing import IO, Any, Callable, Generator, Iterable, Optional

import requests
from requests.exceptions import HTTPError

from unfolded.data_sdk.errors import AuthenticationError, DataSDKError


@contextmanager
def keep_file_position(fileobj: IO[bytes]) -> Generator[None, None, None]:
    """Operate on a file but return to original position"""
    pos = fileobj.tell()
    try:
        yield
    finally:
        fileobj.seek(pos)


def get_fileobj_length(fileobj: IO) -> int:
    """Get length of file object"""
    with keep_file_position(fileobj):
        fileobj.seek(0, os.SEEK_END)
        length = fileobj.tell()
    return length


def read_fileobj_chunks(
    fileobj: IO[bytes], chunk_size: int, callback: Optional[Callable[[int], Any]] = None
) -> Iterable[bytes]:
    """Generator to read a file object by chunks"""
    while True:
        data = fileobj.read(chunk_size)
        if not data:
            break

        if callback:
            callback(len(data))

        yield data


def is_gzipped(fileobj: IO[bytes]) -> bool:
    """Check if file is gzipped by reading magic bytes"""
    with keep_file_position(fileobj):
        fileobj.seek(0)
        is_gzip = fileobj.read(2) == b"\x1f\x8b"
    return is_gzip


# from https://stackoverflow.com/a/24342024
def get_gzip_length(fileobj: IO[bytes]) -> int:
    """Estimate uncompressed size of gzipped file.
    Does not write to disk, instead serially decompresses
    the gzip into a fixed length in-memory buffer.
    """

    READ_CHUNK_SIZE = 1024 * 1024
    MAX_DECOMPRESS_SIZE = 4 * 1024 * 1024

    total_length = 0

    with keep_file_position(fileobj):
        buffer = fileobj.read(READ_CHUNK_SIZE)
        while buffer != b"":  # loop through concatenated gzip streams
            # 15: use a 2**15 size window, 16: expect gzip
            # see https://docs.python.org/3/library/zlib.html#zlib.decompress
            z = zlib.decompressobj(15 + 16)
            while not z.eof:  # loop through one gzip stream
                if buffer == b"":
                    raise ValueError("Incomplete gzip file")
                while buffer != b"":  # go through all output from one input buffer
                    total_length += len(z.decompress(buffer, MAX_DECOMPRESS_SIZE))
                    buffer = z.unconsumed_tail
                buffer = fileobj.read(READ_CHUNK_SIZE)
            buffer = z.unused_data  # get beginning of next gzip file
            if buffer == b"":
                buffer == fileobj.read(READ_CHUNK_SIZE)

        return total_length


# BinaryIO is supposed to be an alias for IO[bytes], but for some reason this
# fails with BinaryIO? Seems related to https://stackoverflow.com/q/62745734 but
# that's supposed to be fixed already.
def compress_fileobj(file_in: IO[bytes], file_out: IO[bytes], **kwargs: Any) -> None:
    """Apply gzip compression to file object

    Args:
        file_in: readable file object (in binary mode) with data to be compressed.
        file_out: writable file object (in binary mode) where compressed data should be written.
        **kwargs: keyword arguments to pass to gzip.open
    """
    with gzip.open(file_out, "wb", **kwargs) as gzipf:
        shutil.copyfileobj(file_in, gzipf)


def raise_for_status(r: requests.Response) -> None:
    """Check valid response, raising custom error for invalid authorization"""
    try:
        r.raise_for_status()
    except HTTPError as e:
        # Re-raise authentication error with better error message
        if r.status_code in (401, 403):
            raise AuthenticationError("Invalid Access Token") from e

        msg: str | None = None
        try:
            msg = r.json()["message"]
        except Exception:
            pass
        if msg is not None:
            raise DataSDKError(msg) from e

        raise e
