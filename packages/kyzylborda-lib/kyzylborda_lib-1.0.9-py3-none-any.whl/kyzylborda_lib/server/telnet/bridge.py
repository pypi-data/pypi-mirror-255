from __future__ import annotations

import asyncio
import signal
from typing import Awaitable, Callable

from .commands import parse_command, IAC, ECHO, SGA, InterruptCommand, OptionDoCommand, OptionWillCommand, SubnegotiationCommand
from .connection import Connection
from ..tcp.bridge import read_chunk_until_writer_closes
from ...sandbox import OneShot


async def bridge_process_to_telnet(stdout: asyncio.StreamReader, connection: Connection):
    try:
        while True:
            buf = await read_chunk_until_writer_closes(stdout, connection.tcp.writer)
            if not buf:
                break
            await connection.writeall(buf)
    except ConnectionResetError:
        pass


async def bridge_telnet_to_process(connection: Connection, process: asyncio.subprocess.Process):
    try:
        while True:
            try:
                buf = await read_chunk_until_writer_closes(connection, process.stdin)
                if not buf:
                    break
                process.stdin.write(buf)
                await process.stdin.drain()
            except InterruptCommand:
                # ^C
                process.stdin.write(b"\x03")
                await process.stdin.drain()
            except OptionDoCommand as e:
                # Whatever they want us to do, we don't support
                await connection.reply_my_option(e.option, False)
            except OptionWillCommand as e:
                # Whatever they want to do, we don't support
                await connection.reply_peer_option(e.option, False)
    except ConnectionResetError:
        pass


async def negotiate(oneshot: OneShot, connection: Connection):
    if oneshot.pty:
        await connection.negotiate_my_option(ECHO, True)
        await connection.negotiate_my_option(SGA, True)
        await connection.negotiate_peer_option(SGA, True)


async def bridge_process(oneshot: OneShot, connection: Connection):
    await asyncio.gather(
        negotiate(oneshot, connection),
        bridge_process_to_telnet(oneshot.process.stdout, connection),
        bridge_telnet_to_process(connection, oneshot.process)
    )
