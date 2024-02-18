from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.style import Style
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.projects import ProjectsAPIClient


class ProjectsDescribeCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ProjectsAPIClient(creds, config_manager)

        result = await client.describe(args.project_id)

        console = Console()

        if result:
            result_info = [
                ("UUID", result.id),
                ("Name", result.name),
                ("Owner", result.owner_id),
                ("Created At", result.created_at),
                ("Updated At", result.updated_at),
            ]

            text = Text()
            for label, value in result_info:
                label_style = Style(color="magenta", bold=True)

                text.append(Text(label + ": ", style=label_style))
                text.append(Text(str(value)))
                text.append("\n")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")

        console.print(text)
