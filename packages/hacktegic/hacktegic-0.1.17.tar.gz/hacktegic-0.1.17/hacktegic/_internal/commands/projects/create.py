from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.projects import ProjectsAPIClient


class ProjectsCreateCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ProjectsAPIClient(creds, config_manager)

        console = Console()

        result = await client.create(args.project_name)

        if result.id:
            text = Text("Project successfully created!")
            text.stylize("bold green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")

        console.print(text)
