import inspect
from typing import Callable, Optional, Sequence

from .client import Client
from .datastructures import Task


class SideKick(Client):
    def __init__(self, tasks: Optional[Sequence[Task]] = None):
        self.tasks = list(tasks) if tasks else []
        super().__init__()

    def add_task(self, func: Callable, *args, **kwargs) -> None:
        task = Task(
            file=inspect.getfile(func),
            func=func.__name__,
            args=args,
            kwargs=kwargs,
        )
        self.tasks.append(task)

    async def process(self, func: Optional[Callable] = None, *args, **kwargs) -> None:
        if func:
            self.add_task(func, *args, **kwargs)
        for task in self.tasks:
            await self.send_task(task)
