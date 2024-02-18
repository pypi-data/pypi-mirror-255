from asyncio import TaskGroup as AsyncTaskGroup, run as async_run
from sys import exit

from hacktegic._internal.parser import ArgumentParser


async def main_async() -> int:
    # try:
    async with AsyncTaskGroup() as tg:
        parser = ArgumentParser(prog="hacktegic")
        parser.add_arguments()
        args = parser.parse_args()
        if hasattr(args, "func"):
            command_task = tg.create_task(args.func(tg, args))
        else:
            parser.print_help()
    return 0


def main() -> int:
    return async_run(main_async())


if __name__ == "__main__":
    exit(main())
