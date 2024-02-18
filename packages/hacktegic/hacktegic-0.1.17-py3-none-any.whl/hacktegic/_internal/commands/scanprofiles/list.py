from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.table import Table
from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.scanprofiles import ScanProfilesAPIClient


class ScanProfilesListCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ScanProfilesAPIClient(creds, config_manager)

        table = Table()
        table.add_column("UUID")
        table.add_column("Title", style="magenta")
        table.add_column("Created At")
        table.add_column("Enabled")
        table.add_column("Schedule")
        table.add_column("Nmap Options")
        table.add_column("Description")

        for i in await client.list():
            table.add_row(i.id, i.title, str(i.created_at), str(i.enabled), str(i.schedule), str(i.nmap_options), str(i.description))
        console = Console()
        console.print(table)