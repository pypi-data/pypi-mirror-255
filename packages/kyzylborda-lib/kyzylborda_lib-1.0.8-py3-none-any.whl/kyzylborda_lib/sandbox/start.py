from __future__ import annotations

import asyncio
import os
from typing import Awaitable, Callable, Optional

from .box import Box, OneShot
from .environment import BoxEnvironment, get_environment, Volume
from ..secrets import get_secret
from ..secrets.encoding import encode_token


__all__ = ("start_box", "stop_box", "start_oneshot")


boxes_by_token: dict[str, dict[str, asyncio.Task[Box]]] = {}


async def _start_kyzylborda_box_process(
    token: str,
    box_env: BoxEnvironment,
    argv: list[str],
    environ: dict[str, str],
    volumes: list[Volume],
    pty: bool
) -> asyncio.subprocess.Process:
    binds = []

    for volume in box_env.volumes + volumes:
        if volume.is_named_volume():
            volume_dir = f"/state/volumes/{encode_token(token)}/{volume.source}"
            os.makedirs(volume_dir, exist_ok=True)
            os.chown(volume_dir, 32768, 32768)
        else:
            volume_dir = os.path.join(box_env.app_root, volume.source)

        bind = f"-b{volume_dir}:{volume.target}"
        if volume.options:
            bind += ":" + volume.options
        binds.append(bind)

    r_fd, w_fd = os.pipe()
    try:
        try:
            process = await asyncio.create_subprocess_exec(
                "kyzylborda-box",
                f"-R{box_env.image_root}",
                *binds,
                f"-s{box_env.size_limit}",
                f"-U{box_env.sandbox_user}",
                f"-G{box_env.sandbox_group}",
                f"-w{box_env.work_dir}",
                f"-M{100 * 1024 * 1024}",
                f"-N{w_fd}",
                *(["-t"] if pty else []),
                *[f"-E{name}={value}" for name, value in {**box_env.environ, **environ}.items()],
                *box_env.argv,
                *argv,
                pass_fds=[w_fd],
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        finally:
            os.close(w_fd)

        # Wait for the sandboxed process to start
        loop = asyncio.get_running_loop()
        ev = asyncio.Event()
        loop.add_reader(r_fd, ev.set)
        await ev.wait()
        loop.remove_reader(r_fd)
    finally:
        os.close(r_fd)

    return process


async def _do_start_box(
    token: str,
    scope: str,
    box_env: BoxEnvironment,
    environ: dict[str, str],
    cleanup_timeout: float,
    init: Optional[Callable[[Box], None | Awaitable[None]]]=None
) -> Box:
    process = await _start_kyzylborda_box_process(token, box_env, [], environ, [], False)
    box = Box(token, scope, process, box_env, cleanup_timeout=cleanup_timeout)

    coro_init = None
    if init is not None:
        future = init(box)
        if future is not None:
            async def go():
                await future
            coro_init = asyncio.create_task(go())

    if box_env.health_checks:
        async def await_all():
            for health_check in box_env.health_checks:
                await health_check.wait(box)

        exit_waiter = asyncio.create_task(process.wait())
        readiness_waiter = asyncio.create_task(await_all())
        finished, not_finished = await asyncio.wait([exit_waiter, readiness_waiter], return_when=asyncio.FIRST_COMPLETED)

        for task in not_finished:
            task.cancel()

        if exit_waiter in finished:
            if coro_init is not None:
                coro_init.cancel()
            exit_code = await exit_waiter
            raise RuntimeError(f"Box exitted with return code {exit_code}")

        if readiness_waiter in finished:
            await readiness_waiter

    if coro_init is not None:
        await coro_init

    return box


def _prepare_environ(
    token: str,
    environ: Optional[dict[str, str]]=None,
    pass_secrets: list[str]=[]
):
    if environ is None:
        environ = {}
    for name in pass_secrets:
        if name == "token":
            value = token
        else:
            value = get_secret(name, token)
        environ[f"KYZYLBORDA_SECRET_{name}"] = value
    return environ


async def start_box(
    token: str,
    scope: Optional[str]=None,
    box_env: Optional[BoxEnvironment | str]=None,
    environ: Optional[dict[str, str]]=None,
    pass_secrets: list[str]=[],
    cleanup_timeout: float = 5 * 60,
    init: Optional[Callable[[Box], None | Awaitable[None]]]=None
) -> Box:
    # scope = "default" and box_env = scope by default, but if scope is not set, box_env is not set either
    if box_env is None:
        box_env = scope
    if scope is None:
        scope = "default"

    if token in boxes_by_token and scope in boxes_by_token[token]:
        try:
            box = await boxes_by_token[token][scope]
        except Exception:
            # e.g. crash
            pass
        else:
            if box.is_stopping():
                await box.stop()
                # Re-create the box
            elif not box.is_alive():
                # e.g. crash
                pass
            else:
                box.cleanup_timeout = max(box.cleanup_timeout, cleanup_timeout)
                return box

    # TODO: verify token?
    environ = _prepare_environ(token, environ, pass_secrets)

    if box_env is None or isinstance(box_env, str):
        box_env = get_environment(box_env)

    box_task = asyncio.create_task(_do_start_box(token, scope, box_env, environ, cleanup_timeout, init))
    if token not in boxes_by_token:
        boxes_by_token[token] = {}
    boxes_by_token[token][scope] = box_task
    return await box_task


async def stop_box(token: str, scope: Optional[str]=None):
    boxes_by_scope = boxes_by_token.get(token, {})

    if scope is None:
        await asyncio.gather(*[stop_box(token, scope) for scope in boxes_by_scope])
        return

    box = await boxes_by_scope[scope]
    await box.stop()


async def start_oneshot(
    token: str,
    scope: Optional[str]=None,
    box_env: Optional[BoxEnvironment | str]=None,
    argv: list[str]=[],
    environ: Optional[dict[str, str]]=None,
    volumes: list[Volume]=[],
    pass_secrets: list[str]=[],
    pty: bool=False
) -> OneShot:
    # scope = "default" and box_env = scope by default, but if scope is not set, box_env is not set either
    if box_env is None:
        box_env = scope
    if scope is None:
        scope = "default"

    # TODO: verify token?
    environ = _prepare_environ(token, environ, pass_secrets)

    if box_env is None or isinstance(box_env, str):
        box_env = get_environment(box_env)

    process = await _start_kyzylborda_box_process(token, box_env, argv, environ, volumes, pty)
    return OneShot(token, scope, process, box_env, pty)
