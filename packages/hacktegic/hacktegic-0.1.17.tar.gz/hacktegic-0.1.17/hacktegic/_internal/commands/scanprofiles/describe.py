from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text
from rich.style import Style

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.scanprofiles import ScanProfilesAPIClient


class ScanProfilesDescribeCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ScanProfilesAPIClient(creds, config_manager)

        console = Console()

        result = await client.describe(args.scanprofile_id)

        if result:
            result_info = [
                ("UUID", result.id),
                ("Name", result.title),
                ("Created At", result.created_at),
                ("Updated At", result.updated_at),
                ("Enabled", result.enabled),
                ("Project ID", result.project_id),
                ("Schedule", result.schedule),
                ("Nmap Options", result.nmap_options),
                ("Description", result.description),
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