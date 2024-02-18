import aiohttp

from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.resources.projects import Project


class ProjectsAPIClient:
    def __init__(self, credentials: Credentials, config_manager: ConfigManager) -> None:
        self.credentials = credentials
        self.config_manager = config_manager

    async def create(self, name: str) -> Project:
        async with aiohttp.ClientSession() as session:
            url = f'{self.config_manager.config["api_base_url"]}v1/general/projects'
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            data = {"name": name}
            async with session.post(url, headers=headers, json=data) as response:
                return Project(**(await response.json()))

    async def list(self) -> list[Project]:
        async with aiohttp.ClientSession() as session:
            url = f'{self.config_manager.config["api_base_url"]}v1/general/projects'
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                return [Project(**i) for i in (await response.json())]

    async def describe(self, project_id: str) -> Project:
        async with aiohttp.ClientSession() as session:
            url = f'{self.config_manager.config["api_base_url"]}v1/general/projects/{project_id}'
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                return Project(**(await response.json()))

    async def update(self, project_id: str, name: str) -> bool:
        async with aiohttp.ClientSession() as session:
            url = f'{self.config_manager.config["api_base_url"]}v1/general/projects/{project_id}'
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            data = {"name": name}
            async with session.patch(url, headers=headers, json=data) as response:
                return response.status == 200

    async def delete(self, project_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            url = f'{self.config_manager.config["api_base_url"]}v1/general/projects/{project_id}'
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.delete(url, headers=headers) as response:
                return response.status == 200
