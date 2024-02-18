from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.api_clients.networks import NetworksAPIClient

class NetworksUpdateCommand(BaseCommand):
    async def run(tg: TaskGroup, args: Namespace) -> None:
        creds = Credentials()
        config_manager = ConfigManager()
        await creds.load()
        await config_manager.load()

        client = NetworksAPIClient(creds, config_manager)

        console = Console()

        update_params = {'address': args.address, 'description': args.description}
        update_params = {k: v for k, v in update_params.items() if v is not None}

        result = await client.update(args.network_id, update_params)

        if result:
            text = Text("Network successfully updated!")
            text.stylize("green")
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")
        console.print(text)