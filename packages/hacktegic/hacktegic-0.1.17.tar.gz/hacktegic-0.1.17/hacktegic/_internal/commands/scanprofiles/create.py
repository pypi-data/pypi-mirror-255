from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.scanprofiles import ScanProfilesAPIClient


class ScanProfilesCreateCommand(BaseCommand):
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

        scanprofile = {"title": args.title}

        if args.description:
            scanprofile["description"] = args.description
        if args.schedule:
            scanprofile["schedule"] = args.schedule
        if args.enabled:
            scanprofile["enabled"] = args.enabled
        if args.nmap_options:
            scanprofile["nmap_options"] = args.nmap_options
        try:
            result = await client.create(scanprofile)
            if result.id:
                text = Text("Scan profile successfully created!")
                text.stylize("green")
            else:
                text = Text("Something went wrong!")
                text.stylize("bold red")
        except KeyError as e:
            text = Text(f"Error: {e}. Please check your configuration.")
            text.stylize("bold red")

        console.print(text)
