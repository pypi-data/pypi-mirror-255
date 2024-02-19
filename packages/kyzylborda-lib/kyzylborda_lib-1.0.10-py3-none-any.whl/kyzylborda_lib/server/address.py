import asyncio
import socket
from typing import Any, Awaitable, Callable

from .. import libc


__all__ = ("parse_address", "stringify_address", "_create_socket")


def parse_address(address: str):
    if address.startswith("netns:"):
        # netns:<path>:<address>
        _, path, address = address.split(":", 2)
        return "netns", (path, address)
    elif address.startswith("unix:"):
        # unix:/path/to/socket
        return "unix", (address[5:],)
    else:
        # localhost:80
        host, port = address.split(":")
        return "ipv4", (host, int(port))


def stringify_address(proto: str, address):
    if proto == "unix":
        if address:
            return f"unix:{address}"
        else:
            return None
    elif proto == "ipv4":
        return f"{address[0]}:{address[1]}"
    else:
        raise NotImplementedError()


def _create_socket(address: str, type: int) -> tuple[socket.socket, Any, Callable[..., Awaitable[Any]]]:
    proto, addr = parse_address(address)

    if proto == "netns":
        with open("/proc/self/ns/net", "rb") as f_self:
            path, address = addr
            with open(path, "rb") as f_other:
                if libc.libc.setns(f_other.fileno(), 0) == -1:
                    err = libc.get_errno()
                    raise OSError(err, libc.strerror(err), "setns failed")

            try:
                return _create_socket(address, type)
            finally:
                if libc.libc.setns(f_self.fileno(), 0) == -1:
                    err = libc.get_errno()
                    raise OSError(err, libc.strerror(err), "setns failed")

    if proto == "unix":
        return socket.socket(socket.AF_UNIX, type, 0), addr[0], asyncio.open_unix_connection

    if proto == "ipv4":
        return socket.socket(socket.AF_INET, type, 0), addr, asyncio.open_connection

    raise ValueError(f"Unsupported protocol {proto}")
