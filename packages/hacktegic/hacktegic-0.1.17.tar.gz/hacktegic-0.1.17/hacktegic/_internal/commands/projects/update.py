from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.projects import ProjectsAPIClient


class ProjectsUpdateCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ProjectsAPIClient(creds, config_manager)

        console = Console()

        result = await client.update(args.project_id, args.name)

        if result:
            text = Text("Project successfully updated!")
            text.stylize("bold green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")
        console.print(text)
