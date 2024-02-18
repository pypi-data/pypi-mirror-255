import asyncio
import socket
import time
from typing import Optional

from ..address import _create_socket


__all__ = ("Connection", "connect")


class Connection:
    def __init__(
        self,
        transport,
        addr,
        unique_ownership: bool,
        server_address: Optional[str]=None,
        peer_address: Optional[str]=None
    ):
        self.transport = transport
        self.addr = addr
        self.unique_ownership = unique_ownership
        self.server_address = server_address
        self.peer_address = peer_address
        self._objects_to_keep_alive = []
        self._queue_start = []
        self._queue_end = asyncio.Queue()
        self._exc = None
        self._expires_at = time.time() + 300

    def keep_object_alive(self, obj):
        self._objects_to_keep_alive.append(obj.__enter__())

    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.close()
            else:
                self.reset()
        except IOError:
            pass
        finally:
            for obj in self._objects_to_keep_alive:
                obj.__exit__(exc_type, exc, tb)

    def unread(self, data: bytes):
        self._queue_start.append(data)

    def _deliver(self, data: bytes):
        self._queue_end.put_nowait(data)
        self._expires_at = time.time() + 300

    async def recv(self) -> bytes:
        if self._exc:
            raise self._exc
        if self._queue_start:
            return self._queue_start.pop()
        else:
            left = self._expires_at - time.time()
            if left <= 0:
                raise ConnectionResetError("Read timeout")
            try:
                return await asyncio.wait_for(self._queue_end.get(), left)
            except TimeoutError:
                raise ConnectionResetError("Read timeout")

    def send(self, data: bytes):
        self.transport.sendto(data, self.addr)
        self._expires_at = time.time() + 300

    def close(self):
        if self.unique_ownership:
            self.transport.close()

    def reset(self):
        if self.unique_ownership:
            self.transport.abort()


class ClientProtocol:
    def __init__(self, conn: Connection):
        self.conn = conn

    def connection_made(self, transport):
        self.conn.transport = transport

    def datagram_received(self, data, addr):
        self.conn._deliver(data)

    def error_received(self, exc):
        self.conn._exc = exc

    def connection_lost(self, exc):
        self.conn._exc = exc


async def connect(address: str) -> Connection:
    sock, addr, _ = _create_socket(address, socket.SOCK_DGRAM)
    conn = Connection(None, addr, True)

    loop = asyncio.get_running_loop()

    try:
        sock.setblocking(False)
        await loop.create_datagram_endpoint(lambda: ClientProtocol(conn), sock=sock)
    except Exception:
        sock.close()
        raise

    return conn
