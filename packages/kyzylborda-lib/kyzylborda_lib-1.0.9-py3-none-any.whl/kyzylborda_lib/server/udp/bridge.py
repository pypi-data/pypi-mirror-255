import asyncio
from .connection import Connection


__all__ = ("bridge_connections_unidirectional", "bridge_connections")


async def bridge_connections_unidirectional(a: Connection, b: Connection):
    try:
        while True:
            b.send(await a.recv())
    except ConnectionResetError:
        pass


async def bridge_connections(a: Connection, b: Connection):
    await asyncio.gather(bridge_connections_unidirectional(a, b), bridge_connections_unidirectional(b, a))
