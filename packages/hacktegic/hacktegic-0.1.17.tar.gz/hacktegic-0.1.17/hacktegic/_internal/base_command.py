from asyncio import TaskGroup
from argparse import Namespace


class BaseCommand:
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        pass
