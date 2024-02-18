from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.networks import NetworksAPIClient

class NetworksDeleteCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = NetworksAPIClient(creds, config_manager)

        result = await client.delete(args.network_id)

        if result:
            text = Text("Network successfully deleted!")
            text.stylize("green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")
        console = Console()
        console.print(text)
