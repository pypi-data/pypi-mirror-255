from __future__ import annotations

import asyncio
from typing import Optional, TypeVar

from ..tcp.connection import Connection
from .commands import IAC, WILL, WONT, DO, DONT, SB, SE, NEW_ENVIRON, NEW_ENVIRON_IS, NEW_ENVIRON_SEND, NEW_ENVIRON_VAR, NEW_ENVIRON_VALUE, NEW_ENVIRON_ESC, NEW_ENVIRON_USERVAR, parse_command, OptionDoCommand, OptionWillCommand, SubnegotiationCommand, NopCommand


T = TypeVar("T")


class Connection:
    tcp: Connection

    def __init__(self, tcp: Connection):
        self.tcp = tcp
        self.my_options = {}
        self.peer_options = {}
        self.my_options_events = {}
        self.peer_options_events = {}
        self.environ_event = None
        self.environ_var = None
        self.environ_uservar = None

    def unread(self, data: bytes):
        # Escape IAC
        self.tcp.write(data.replace(b"\xff", b"\xff\xff"))

    async def read(self, n: int) -> bytes:
        # We can't handle n == -1 here yet
        assert n >= 0

        while True:
            buf = await self.tcp.read(n)
            if not buf:
                return buf

            iac_index = buf.find(IAC)
            if iac_index == -1:
                iac_index = len(buf)

            if iac_index > 0:
                self.tcp.unread(buf[iac_index:])
                buf = buf[:iac_index]
                # CR LF = LF, CR NUL = CR
                if buf.endswith(b"\r"):
                    buf += await self.tcp.read(1)
                buf = buf.replace(b"\r\n", b"\n").replace(b"\r\0", b"\r")
                return buf

            command, buf = await parse_command(buf, self.tcp.reader)
            self.tcp.unread(buf)

            if isinstance(command, OptionDoCommand):
                if command.option in self.my_options_events:
                    self.my_options[command.option] = command.mode
                    self.my_options_events[command.option].set()
                    continue
                else:
                    # If they want us to set an option that is already in the same
                    # state, ignore the command
                    if self.my_options.get(command.option, False) == command.mode:
                        continue
            elif isinstance(command, OptionWillCommand):
                if command.option in self.peer_options_events:
                    self.peer_options[command.option] = command.mode
                    self.peer_options_events[command.option].set()
                    continue
                else:
                    # If they want to set an option that is already in the same
                    # state, ignore the command
                    if self.peer_options.get(command.option, False) == command.mode:
                        continue
            elif isinstance(command, SubnegotiationCommand):
                if command.option == NEW_ENVIRON:
                    self.handle_environ_subnegotiation(command.data)
                continue
            elif isinstance(command, NopCommand):
                continue

            raise command

    def write(self, data: bytes):
        # Escape IAC
        self.tcp.write(data.replace(b"\xff", b"\xff\xff"))
    async def writeall(self, data: bytes):
        self.write(data)
        await self.drain()
    async def drain(self):
        await self.tcp.drain()

    async def reply_my_option(self, option: int, mode: bool):
        self.my_options[option] = mode
        await self.tcp.writeall(bytes([IAC, WILL if mode else WONT, option]))
    async def reply_peer_option(self, option: int, mode: bool):
        self.peer_options[option] = mode
        await self.tcp.writeall(bytes([IAC, DO if mode else DONT, option]))

    # Return whether negotiation was successful. Should only be run while another
    # is in a read() loop
    async def negotiate_my_option(self, option: int, mode: bool) -> bool:
        if self.my_options.get(option, False) == mode:
            return True
        if option in self.my_options_events:
            raise ValueError("This option is already being negotiated")
        event = asyncio.Event()
        self.my_options_events[option] = event
        await self.tcp.writeall(bytes([IAC, WILL if mode else WONT, option]))
        await event.wait()
        del self.my_options_events[option]
        return self.my_options[option] == mode
    async def negotiate_peer_option(self, option: int, mode: bool) -> bool:
        if self.peer_options.get(option, False) == mode:
            return True
        if option in self.peer_options_events:
            raise ValueError("This option is already being negotiated")
        event = asyncio.Event()
        self.peer_options_events[option] = event
        await self.tcp.writeall(bytes([IAC, DO if mode else DONT, option]))
        await event.wait()
        del self.peer_options_events[option]
        return self.peer_options[option] == mode

    async def subnegotiate(self, option: int, data: bytes):
        # Escape IAC
        data = data.replace(b"\xff", b"\xff\xff")
        await self.tcp.writeall(bytes([IAC, SB, option]) + data + bytes([IAC, SE]))

    def handle_environ_subnegotiation(self, data: bytes):
        if not data:
            return
        if data[0] != NEW_ENVIRON_IS:
            return
        i = 1
        var = {}
        uservar = {}
        while i < len(data):
            if data[i] == NEW_ENVIRON_VAR:
                is_user_var = False
            elif data[i] == NEW_ENVIRON_USERVAR:
                is_user_var = True
            else:
                return
            i += 1
            name = bytearray()
            value = None
            target = name
            while i < len(data):
                if data[i] == NEW_ENVIRON_ESC and i + 1 < len(data):
                    target.append(data[i + 1])
                    i += 2
                elif data[i] == NEW_ENVIRON_VALUE:
                    value = bytearray()
                    target = value
                    i += 1
                elif data[i] in (NEW_ENVIRON_VAR, NEW_ENVIRON_USERVAR):
                    break
                else:
                    target.append(data[i])
                    i += 1
            name = name.decode(errors="ignore")
            if value is not None:
                value = value.decode(errors="ignore")
            if is_user_var:
                uservar[name] = value
            else:
                var[name] = value
        self.environ_var = var
        self.environ_uservar = uservar
        if self.environ_event:
            self.environ_event.set()

    async def get_env_var(self, name: str, user: bool) -> Optional[str]:
        if self.environ_var is None:
            if not await self.negotiate_peer_option(NEW_ENVIRON, True):
                return None
            if self.environ_event is None:
                self.environ_event = asyncio.Event()
                await self.subnegotiate(NEW_ENVIRON, bytes([NEW_ENVIRON_SEND, NEW_ENVIRON_VAR, NEW_ENVIRON_USERVAR]))
            await self.environ_event.wait()
            self.environ_event = None
        if user:
            return self.environ_uservar.get(name)
        else:
            return self.environ_var.get(name)

    async def get_user(self) -> Optional[str]:
        return await self.get_env_var("USER", user=False)


    async def with_buffering(self, awaitable: Awaitable[T]) -> T:
        task = asyncio.create_task(awaitable)
        task_read = asyncio.create_task(self.read(4096))

        to_unread = bytearray()

        while True:
            finished, not_finished = await asyncio.wait([task, task_read], return_when=asyncio.FIRST_COMPLETED)
            if task in finished:
                break
            to_unread += await task_read
            task_read = asyncio.create_task(self.read(4096))

        if task_read in finished:
            to_unread += await task_read
        else:
            task_read.cancel()
        self.unread(to_unread)
        return await task



    # async def readline(self) -> bytes:
    #     return await self.reader.readline()
    # async def readexactly(self, n: int) -> bytes:
    #     return await self.reader.readexactly(n)
    # async def readuntil(self, separator: bytes) -> bytes:
    #     return await self.reader.readuntil(separator)

    # def writelines(self, data: Iterable[bytes]):
    #     self.writer.writelines(data)
    # def write_eof(self):
    #     self.writer.write_eof()
    # async def writeall(self, data: bytes):
    #     self.write(data)
    #     await self.drain()
