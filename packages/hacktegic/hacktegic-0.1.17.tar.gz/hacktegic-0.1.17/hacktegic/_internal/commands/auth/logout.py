from argparse import Namespace

from asyncio import TaskGroup

from rich.console import Console
from rich.text import Text


from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.credentials import Credentials


class LogoutCommand(BaseCommand):
    @staticmethod
    async def run(tg: TaskGroup, args: Namespace) -> None:
        console = Console()

        creds = Credentials()
        await creds.load()

        if not await creds.authenticated():
            text = Text("You are already logged out!")
            text.stylize("bold green")
            console.print(text)

        else:
            remove = await creds.remove()
            if remove:
                text = Text("You are now logged out!")
                text.stylize("bold green")
                console.print(text)

            else:
                console.print("Something went wrong!. Please try again.")
