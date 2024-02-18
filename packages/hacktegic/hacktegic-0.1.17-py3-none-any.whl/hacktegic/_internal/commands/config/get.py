from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text
from tomlkit.exceptions import NonExistentKey

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager


class ConfigGetCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        console = Console()

        config_manager = ConfigManager()

        await config_manager.load()

        try:
            val = config_manager.config[args.key]
        except NonExistentKey:
            text = Text(f'Key "{args.key}" does not exist!')
            text.stylize("bold red")
            console.print(text)
            return

        console.print(val)
