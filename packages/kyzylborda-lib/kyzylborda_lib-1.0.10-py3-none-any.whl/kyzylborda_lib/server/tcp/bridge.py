import asyncio
from .connection import Connection


__all__ = (
    "read_chunk_until_writer_closes",
    "bridge_connections_unidirectional",
    "bridge_connections"
)


async def read_chunk_until_writer_closes(reader, task_closed) -> bytes:
    # Wait for writer's close simultaneously with data to write, so that we can terminate the read
    # end immediately after the write end dies
    task_read = asyncio.create_task(reader.read(16384))
    done, pending = await asyncio.wait(
        [task_read, task_closed],
        return_when=asyncio.FIRST_COMPLETED
    )
    if task_read in done:
        return await task_read
    else:
        task_read.cancel()
        await task_closed
        return b""


async def bridge_connections_unidirectional(a: Connection, b: Connection):
    task_closed = asyncio.create_task(b.writer.wait_closed())
    try:
        while True:
            buf = await read_chunk_until_writer_closes(a.reader, task_closed)
            if not buf:
                b.writer.write_eof()
                b.writer.close()
                break
            b.writer.write(buf)
            await b.writer.drain()
    except ConnectionResetError:
        pass
    finally:
        await task_closed


async def bridge_connections(a: Connection, b: Connection):
    await asyncio.gather(bridge_connections_unidirectional(a, b), bridge_connections_unidirectional(b, a))
