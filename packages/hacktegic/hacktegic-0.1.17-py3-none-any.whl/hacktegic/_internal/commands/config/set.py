from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager


class ConfigSetCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        console = Console()

        config_manager = ConfigManager()
        await config_manager.load()

        config_manager.config[args.key] = args.value

        await config_manager.save()

        text = Text(f'Set "{args.key}" to "{args.value}"')
        text.stylize("bold green")
        console.print(text)
