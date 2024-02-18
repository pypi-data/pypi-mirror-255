import asyncio
from braceexpand import braceexpand
import os
import socket
import traceback

from . import HandlerType
from ..address import parse_address, stringify_address, _create_socket
from .bridge import bridge_connections
from .connection import Connection, connect
from ...sandbox import Box


__all__ = ("ReverseProxy",)


class Protocol:
    def __init__(self, _server_address: str, proto: str, proxy: "ReverseProxy"):
        self._server_address = _server_address
        self._proto = proto
        self._proxy = proxy
        self._connections = {}


    def connection_made(self, transport):
        self._transport = transport


    def datagram_received(self, data, addr):
        new = addr not in self._connections

        if new:
            self._connections[addr] = Connection(
                self._transport,
                addr,
                False,
                server_address=self._server_address,
                peer_address=stringify_address(self._proto, addr)
            )

        conn = self._connections[addr]
        conn._deliver(data)

        if new:
            task = asyncio.create_task(self._handle_connection(conn))
            self._proxy._running_tasks.add(task)
            task.add_done_callback(lambda t: self._proxy._running_tasks.remove(t))


    async def _handle_connection(self, conn: Connection):
        try:
            ret = await self._proxy._handler(conn)

            if ret is not None:
                if isinstance(ret, Box):
                    box = ret
                    with box.borrow():
                        address = box.get_socket_address()
                        if address is None:
                            raise ValueError(f"Box {box} does not bind to a socket--check kyzylborda-box.yml.")
                        ret = await connect(address)
                        ret.keep_object_alive(box.borrow())

                if isinstance(ret, str):
                    ret = await connect(ret)

                if isinstance(ret, Connection):
                    async with ret:
                        await bridge_connections(conn, ret)
                else:
                    raise TypeError("Return value of a handler must be None, a Connection, an address, or a Box")

        except Exception:
            traceback.print_exc()

        finally:
            del self._connections[conn.addr]


class ReverseProxy:
    def __init__(self, handler: HandlerType):
        self._handler = handler
        self._running_tasks = set()


    async def listen(self, address_mask: str):
        async def start_server(address: str):
            proto, addr = parse_address(address)
            sock, _, _ = _create_socket(address, socket.SOCK_DGRAM)

            try:
                sock.setblocking(False)
                sock.bind(addr)
                if proto == "unix":
                    os.chmod(*addr, 0o777)

                loop = asyncio.get_running_loop()
                await loop.create_datagram_endpoint(lambda: Protocol(address, proto, self), sock=sock)
            except Exception:
                sock.close()
                raise

        await asyncio.gather(*[start_server(address) for address in braceexpand(address_mask)])

        print("Listening on", address_mask, flush=True)

        while True:
            await asyncio.sleep(3600)
