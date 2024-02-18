from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.table import Table

from hacktegic._internal.base_command import BaseCommand
from hacktegic.cloud.api_clients.scanprofiles import ScanProfilesAPIClient
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials


class ScanProfilesNetworksListCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ScanProfilesAPIClient(creds, config_manager)

        table = Table()
        table.add_column("UUID")
        table.add_column("Address", style="magenta")
        table.add_column("Created At")

        for i in await client.networks_list(args.scanprofile_id):
            table.add_row(i["id"], i["address"], str(i["created_at"]))
        console = Console()
        console.print(table)