import asyncio
import socket
import struct
from typing import Iterable, Optional

from ..address import _create_socket


__all__ = ("Connection", "connect")


class Connection:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        server_address: Optional[str]=None,
        peer_address: Optional[str]=None
    ):
        self.reader = reader
        self.writer = writer
        self.server_address = server_address
        self.peer_address = peer_address
        self._objects_to_keep_alive = []

    def keep_object_alive(self, obj):
        self._objects_to_keep_alive.append(obj.__enter__())

    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                await self.drain()
                self.write_eof()
                self.close()
            else:
                self.reset()
        except IOError:
            pass
        finally:
            for obj in self._objects_to_keep_alive:
                obj.__exit__(exc_type, exc, tb)

    def unread(self, data: bytes | bytearray):
        self.reader._buffer = bytearray(data + self.reader._buffer)

    async def read(self, n: int=-1) -> bytes:
        return await self.reader.read(n)
    async def readline(self) -> bytes:
        return await self.reader.readline()
    async def readexactly(self, n: int) -> bytes:
        return await self.reader.readexactly(n)
    async def readuntil(self, separator: bytes) -> bytes:
        return await self.reader.readuntil(separator)

    def write(self, data: bytes):
        self.writer.write(data)
    def writelines(self, data: Iterable[bytes]):
        self.writer.writelines(data)
    async def drain(self):
        await self.writer.drain()
    def write_eof(self):
        self.writer.write_eof()
    async def writeall(self, data: bytes):
        self.write(data)
        await self.drain()

    def close(self):
        self.writer.close()

    def reset(self):
        if self.writer._transport._sock:
            self.writer._transport._sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
            self.close()


async def connect(address: str) -> Connection:
    sock, addr, do_connect = _create_socket(address, socket.SOCK_STREAM)

    loop = asyncio.get_running_loop()

    try:
        sock.setblocking(False)
        await loop.sock_connect(sock, addr)
    except Exception:
        sock.close()
        raise

    reader, writer = await do_connect(sock=sock, limit=4 * 1024)
    return Connection(reader, writer)
