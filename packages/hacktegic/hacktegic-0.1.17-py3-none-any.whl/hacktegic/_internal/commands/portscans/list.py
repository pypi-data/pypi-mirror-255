from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.table import Table


from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.portscans import PortScansAPIClient

class PortScansListCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = PortScansAPIClient(creds, config_manager)
        console = Console()

        table = Table()
        table.add_column("UUID")
        table.add_column("status", style="magenta")
        table.add_column("Created At")
        table.add_column("Updated At")
        table.add_column("scan_profile_id")

        for i in await client.list():
            table.add_row(i.id, i.status, str(i.created_at), str(i.updated_at), i.scan_profile_id)
        console.print(table)

