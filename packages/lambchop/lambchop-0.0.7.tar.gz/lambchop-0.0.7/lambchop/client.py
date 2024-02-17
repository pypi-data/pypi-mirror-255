from typing import Any

import anyio
import dill

from .datastructures import Task


class Client:
    def __init__(self, port: int = 1956):
        self.port = port

    def serialize(self, task: Task) -> bytes:
        """Convert python function and parameters"""
        return dill.dumps(task)

    def deserialize(self, result: bytes) -> Any:
        return dill.loads(result)

    async def ping(self):
        """Send name to TCP server."""
        async with await anyio.connect_tcp("localhost", self.port) as client:
            await client.send(b"PING")
            return await client.receive()

    async def send_task(self, task: Task):
        """Send task to TCP server."""
        bt = self.serialize(task)
        async with await anyio.connect_tcp("localhost", self.port) as client:
            await client.send(bt)
