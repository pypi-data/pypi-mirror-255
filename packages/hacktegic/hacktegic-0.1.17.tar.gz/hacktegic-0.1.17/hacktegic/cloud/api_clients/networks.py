import aiohttp

from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.resources.networks import Networks


class NetworksAPIClient:
    def __init__(self, credentials: Credentials, config_manager: ConfigManager) -> None:
        self.credentials = credentials
        self.config_manager = config_manager

    async def create(self, asset_cidr: dict) -> Networks:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/assets/cidr"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.post(url, headers=headers, json=asset_cidr) as response:
                return Networks(**(await response.json()))

    async def list(self) -> list[Networks]:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/assets/cidr"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                return [Networks(**i) for i in (await response.json())]

    async def describe(self, asset_cidr_id: str) -> Networks:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/assets/cidr/{asset_cidr_id}"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                return Networks(**(await response.json()))

    async def update(self, asset_cidr_id: str, asset_cidr: dict) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/assets/cidr/{asset_cidr_id}"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.put(url, headers=headers, json=asset_cidr) as response:
                return response.status == 200

    async def delete(self, asset_cidr_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/assets/cidr/{asset_cidr_id}"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.delete(url, headers=headers) as response:
                return response.status == 200
