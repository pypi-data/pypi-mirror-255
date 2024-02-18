import webbrowser
from argparse import Namespace
from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials


class RegisterCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        console = Console()

        try:
            config_manager = ConfigManager()
            await config_manager.load()
            creds = Credentials()
            await creds.load()

            register_url = f"{config_manager.config['api_base_url']}register"

            if await creds.authenticated():
                text = Text("You seem to already have an account.")
                text.stylize("bold green")
                console.print(text)
                console.print("If you want to register again, log out first using using 'hacktegic auth logout'.")

            else:
                webbrowser.open(register_url)
                console.print("Use the web browser to register.")
                console.print(f"If it did not open for you navigate to {register_url} .")
                return
        except:
            text = Text("Something went wrong!")
            text.stylize("bold red")
            console.print(text)
