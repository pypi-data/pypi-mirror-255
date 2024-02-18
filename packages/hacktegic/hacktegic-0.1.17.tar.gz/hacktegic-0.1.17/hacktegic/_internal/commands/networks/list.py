from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.table import Table

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.networks import NetworksAPIClient

class NetworksListCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()

        await creds.load()
        await config_manager.load()

        client = NetworksAPIClient(creds, config_manager)

        table = Table()
        table.add_column("UUID")
        table.add_column("Address", style="magenta")
        table.add_column("Description")
        table.add_column("Created At")

        for i in await client.list():
            table.add_row(i.id, i.address, i.description, str(i.created_at))
        console = Console()
        console.print(table)