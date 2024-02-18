from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.projects import ProjectsAPIClient


class ProjectsDeleteCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ProjectsAPIClient(creds, config_manager)

        results = await client.delete(args.project_id)

        if results:
            text = Text("Project successfully deleted!")
            text.stylize("bold green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")
        console = Console()
        console.print(text)
