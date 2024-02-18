from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.table import Table

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.projects import ProjectsAPIClient


class ProjectsListCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ProjectsAPIClient(creds, config_manager)

        table = Table()
        table.add_column("UUID")
        table.add_column("Name", style="magenta")
        table.add_column("Created At")

        for i in await client.list():
            table.add_row(i.id, i.name, str(i.created_at))
        console = Console()
        console.print(table)
