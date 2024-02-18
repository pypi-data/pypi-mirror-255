import asyncio
from dataclasses import dataclass


__all__ = (
    "parse_command",
    "IAC", "ECHO",
    "InterruptCommand", "OptionDoCommand", "OptionWillCommand", "SubnegotiationCommand", "NopCommand",
    "Command",
)


SE = 240
NOP = 241
DM = 242
BRK = 243
IP = 244
AO = 245
AYT = 246
EC = 247
EL = 248
GA = 249
SB = 250
WILL = 251
WONT = 252
DO = 253
DONT = 254
IAC = 255

ECHO = 1
SGA = 3
NEW_ENVIRON = 39

NEW_ENVIRON_IS = 0
NEW_ENVIRON_SEND = 1
NEW_ENVIRON_INFO = 2
NEW_ENVIRON_VAR = 0
NEW_ENVIRON_VALUE = 1
NEW_ENVIRON_ESC = 2
NEW_ENVIRON_USERVAR = 3


class BaseCommand(BaseException):
    pass

class InterruptCommand(BaseCommand):
    pass

@dataclass
class OptionDoCommand(BaseCommand):
    option: int
    mode: bool

@dataclass
class OptionWillCommand(BaseCommand):
    option: int
    mode: bool

@dataclass
class SubnegotiationCommand(BaseCommand):
    option: int
    data: bytes

class NopCommand(BaseCommand):
    pass

Command = InterruptCommand | OptionDoCommand | OptionWillCommand | SubnegotiationCommand | NopCommand


# buf must start with IAC
async def parse_command(buf: bytes, reader: asyncio.StreamReader) -> (Command, bytes):
    index_in_buf = 0
    async def getc() -> int:
        nonlocal buf, index_in_buf
        if index_in_buf < len(buf):
            index_in_buf += 1
        else:
            buf = await reader.read(16384)
            if not buf:
                raise EOFError("Unexpected EOF in a TELNET command")
            index_in_buf = 1
        return buf[index_in_buf - 1]


    assert await getc() == IAC
    c = await getc()
    if c == IP:
        command = InterruptCommand()
    elif c == DO:
        command = OptionDoCommand(await getc(), True)
    elif c == DONT:
        command = OptionDoCommand(await getc(), False)
    elif c == WILL:
        command = OptionWillCommand(await getc(), True)
    elif c == WONT:
        command = OptionWillCommand(await getc(), False)
    elif c == SB:
        option = await getc()
        data = bytearray()
        while True:
            c = await getc()
            if c != IAC:
                data.append(c)
                continue
            c = await getc()
            if c == IAC:
                data.append(c)
            elif c == SE:
                break
            else:
                # Unexpected, just swallow
                continue
        command = SubnegotiationCommand(option, bytes(data))
    else:
        # Something we don't want to handle in any way
        command = NopCommand()

    return command, buf[index_in_buf:]
