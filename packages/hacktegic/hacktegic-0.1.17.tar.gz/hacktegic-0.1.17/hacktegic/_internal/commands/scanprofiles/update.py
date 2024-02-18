from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.scanprofiles import ScanProfilesAPIClient


class ScanProfilesUpdateCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = ScanProfilesAPIClient(creds, config_manager)

        console = Console()

        if args.enabled is None:
            args.enabled = True
        update_params = {'title': args.title, 'schedule': args.schedule, 'enabled': bool(args.enabled), 'nmap_options': args.nmap_options, 'description': args.description}
        update_params = {k: v for k, v in update_params.items() if v is not None}
        result = await client.update(args.scanprofile_id, update_params)

        if result:
            text = Text("Scan profile successfully updated!")
            text.stylize("bold green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")

        console.print(text)