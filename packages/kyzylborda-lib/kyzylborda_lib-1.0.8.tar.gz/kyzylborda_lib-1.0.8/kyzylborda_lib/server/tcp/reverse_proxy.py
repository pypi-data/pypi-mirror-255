import asyncio
from braceexpand import braceexpand
import os
import traceback

from . import HandlerType
from ..address import parse_address, stringify_address
from .bridge import bridge_connections
from .connection import Connection, connect
from ...sandbox import Box, OneShot


__all__ = ("ReverseProxy",)


class ReverseProxy:
    def __init__(self, handler: HandlerType):
        self._handler = handler
        self._running_tasks = set()


    async def _handle_connection_impl(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server_address: str, proto: str):
        peer_address = stringify_address(proto, writer.get_extra_info("peername"))
        async with Connection(reader, writer, server_address=server_address, peer_address=peer_address) as conn:
            ret = await self._handler(conn)

            if ret is not None:
                if isinstance(ret, Box):
                    box = ret
                    with box.borrow():
                        address = box.get_socket_address()
                        if address is None:
                            raise ValueError(f"Box {box} does not bind to a socket--check kyzylborda-box.yml.")
                        ret = await connect(address)
                        ret.keep_object_alive(box.borrow())

                if isinstance(ret, OneShot):
                    oneshot = ret
                    ret = Connection(oneshot.process.stdout, oneshot.process.stdin)

                if isinstance(ret, str):
                    ret = await connect(ret)

                if isinstance(ret, Connection):
                    async with ret:
                        await bridge_connections(conn, ret)
                else:
                    raise TypeError("Return value of a handler must be None, a Connection, an address, or a Box")


    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server_address: str, proto: str):
        task = asyncio.create_task(self._handle_connection_impl(reader, writer, server_address, proto))
        self._running_tasks.add(task)
        task.add_done_callback(lambda t: self._running_tasks.remove(t))
        try:
            await task
        except Exception:
            traceback.print_exc()


    async def listen(self, address_mask: str):
        servers = []

        async def install_server(address: str):
            proto, addr = parse_address(address)
            if proto == "unix":
                start = asyncio.start_unix_server
            elif proto == "ipv4":
                start = asyncio.start_server
            else:
                raise ValueError(f"Unsupported protocol {proto}")
            server = await start(
                lambda reader, writer: self._handle_connection(reader, writer, address, proto),
                *addr,
                limit=4 * 1024
            )
            if proto == "unix":
                os.chmod(*addr, 0o777)
            servers.append(server)

        await asyncio.gather(*[install_server(address) for address in braceexpand(address_mask)])

        print("Listening on", address_mask, flush=True)

        await asyncio.gather(*[server.serve_forever() for server in servers])
