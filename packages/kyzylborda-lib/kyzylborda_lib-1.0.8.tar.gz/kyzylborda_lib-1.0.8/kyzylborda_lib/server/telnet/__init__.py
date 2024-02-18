from __future__ import annotations

import traceback
from typing import Awaitable, Callable, Optional, TYPE_CHECKING

from .bridge import bridge_process
from .connection import Connection
from ...sandbox import OneShot
from .. import tcp


__all__ = ("HandlerType", "listen", "Connection")


if TYPE_CHECKING:
    HandlerType = Callable[[Connection], Awaitable[OneShot | None]]
else:
    HandlerType = None


def listen(handler: Optional[HandlerType]):
    @tcp.listen
    async def wrapped(connection: tcp.Connection):
        connection = Connection(connection)

        try:
            ret = await handler(connection)
        except Exception:
            traceback.print_exc()
            return

        if ret is None:
            return

        if isinstance(ret, OneShot):
            await bridge_process(ret, connection)
