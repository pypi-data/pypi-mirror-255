import argparse
import asyncio
import base64
import hashlib
import os
import random
import webbrowser

import requests
from aiohttp import web
from rich.console import Console
from rich.text import Text

from hacktegic._internal.base_command import BaseCommand
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials

console = Console()

routes = web.RouteTableDef()

oauth_action_event = asyncio.Event()

port = random.randint(1024, 65535)

code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("utf-8")

code_challenge = (
    base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
    .decode("utf-8")
    .rstrip("=")
)

oauth_params = {
    "code_verifier": code_verifier,
    "redirect_uri": f"http://127.0.0.1:{port}/auth/callback",
}


class LoginCommand(BaseCommand):
    @staticmethod
    @routes.get("/auth/callback")
    async def oauth_handler(request: web.Request):
        config_manager = ConfigManager()
        await config_manager.load()

        oauth_action_event.set()

        if request.query.get("error_description"):
            text = Text(request.query.get("error_description"))
            text.stylize("bold red")
            console.print(text)
            return web.Response(
                status=302,
                content_type="text/plain",
                headers={
                    "Location": f'{config_manager.config["api_base_url"]}dashboard'
                },
            )

        # TODO: verify state
        code = request.query.get("code")
        code_verifier_bytes = oauth_params["code_verifier"].encode("utf-8")
        # TODO: rewrite to use aiohttp
        response = requests.post(
            f'{config_manager.config["api_base_url"]}oauth/token',
            data={
                "grant_type": "authorization_code",
                "client_id": config_manager.config["oauth_client_id"],
                "redirect_uri": oauth_params["redirect_uri"],
                "code_verifier": code_verifier_bytes,
                "code": code,
            },
        )

        if response.ok:
            json_response = response.json()
            text = Text("You are now logged in!")
            text.stylize("bold green")
            console.print(text)
            creds = Credentials(
                json_response["access_token"], json_response["refresh_token"]
            )
            await creds.save()
            # print(json_response.get("access_token"))
        else:
            text = Text("Something went wrong!")
            text.stylize("bold red")
            console.print(text)

        return web.Response(
            status=302,
            content_type="text/plain",
            headers={"Location": f'{config_manager.config["api_base_url"]}dashboard'},
        )

    @staticmethod
    async def run(tg: asyncio.TaskGroup, args: argparse.Namespace) -> None:
        config_manager = ConfigManager()
        creds = Credentials()
        await asyncio.gather(config_manager.load(), creds.load())

        if await creds.authenticated():
            text = Text("You are already logged in!")
            text.stylize("bold green")
            console.print(text)
            return
        state = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")

        app = web.Application()
        app.add_routes(routes)

        params = {
            "client_id": config_manager.config["oauth_client_id"],
            "redirect_uri": oauth_params["redirect_uri"],
            "response_type": "code",
            "scope": "",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "prompt": "consent",
        }

        query = "&".join(f"{key}={value}" for key, value in params.items())
        auth_url = f'{config_manager.config["api_base_url"]}oauth/authorize?{query}'

        print(
            f"Use the web browser to log in.\n\nIf it did not open for you, navigate to {auth_url} .\n"
        )

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="127.0.0.1", port=port)
        tcpsite_task = tg.create_task(site.start())
        webbrowser.open(auth_url)
        await oauth_action_event.wait()
        await runner.server.shutdown(timeout=9)
        tcpsite_task.cancel()
        await tcpsite_task
