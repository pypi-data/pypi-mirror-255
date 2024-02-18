from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.portscans import PortScansAPIClient

class PortScansDeleteCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = PortScansAPIClient(creds, config_manager)
        console = Console()

        result = await client.delete(args.portscan_id)

        if result:
            text = Text("Scan successfully deleted!")
            text.stylize("green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")

        console.print(text)