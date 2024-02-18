from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic.cloud.api_clients.scanprofiles import ScanProfilesAPIClient
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials


class ScanProfilesNetworksAttachCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ScanProfilesAPIClient(creds, config_manager)

        console = Console()

        result = await client.networks_attach(args.scanprofile_id, args.network_id)

        if result:
            text = Text("Network successfully attached!")
            text.stylize("green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")

        console.print(text)