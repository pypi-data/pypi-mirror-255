import aiohttp
from typing import List
from hacktegic._internal.config import ConfigManager
from hacktegic._internal.credentials import Credentials
from hacktegic.cloud.resources.scanprofiles import ScanProfile


class ScanProfilesAPIClient:
    def __init__(self, credentials: Credentials, config_manager: ConfigManager) -> None:
        self.credentials = credentials
        self.config_manager = config_manager

    async def create(self, scanprofile: dict) -> ScanProfile:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.post(url, headers=headers, json=scanprofile) as response:
                response.raise_for_status()

                try:
                    return ScanProfile(**(await response.json()))
                except aiohttp.ContentTypeError:
                    print("Non-JSON response:", await response.text())
                    raise

    async def list(self) -> list[ScanProfile]:
        async with aiohttp.ClientSession() as session:
            url = f'{self.config_manager.config["api_base_url"]}v1/general/projects/{self.config_manager.config["project_id"]}/scan_profiles'
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                return [ScanProfile(**i) for i in (await response.json())]

    async def describe(self, scanprofile_id: str) -> ScanProfile:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                json_data = await response.json()

                return ScanProfile(**json_data)

    async def update(self, scanprofile_id: str, scanprofile: dict) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}

            async with session.put(url, headers=headers, json=scanprofile) as response:
                result = response.status == 200

            return result

    async def delete(self, scanprofile_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.delete(url, headers=headers) as response:
                return response.status == 200

    async def networks_list(self, scanprofile_id: str) -> List[dict]:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}/assets/cidr"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
            async with session.get(url, headers=headers) as response:
                return await response.json()

    async def networks_attach(self, scanprofile_id: str, assets_cidr_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}/assets/cidr/{assets_cidr_id}/attach"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}

            try:
                async with session.post(url, headers=headers) as response:
                    response.raise_for_status()
                    return response.status == 200
            except aiohttp.ClientResponseError as cre:
                print(f"HTTP error occurred: {cre.status}, message='{cre.message}', url={cre.request_info.url}")
                return False
            except Exception as e:
                print(f"An error occurred: {e}")
                return False

    async def networks_detach(self, scanprofile_id: str, assets_cidr_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}/assets/cidr/{assets_cidr_id}/detach"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}

            try:
                async with session.post(url, headers=headers) as response:
                    response.raise_for_status()
                    return response.status == 200
            except aiohttp.ClientResponseError as cre:
                print(f"HTTP error occurred: {cre.status}, message='{cre.message}', url={cre.request_info.url}")
                return False
            except Exception as e:
                print(f"An error occurred: {e}")
                return False

    async def scan(self, scanprofile_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            base_url = self.config_manager.config["api_base_url"]
            project_id = self.config_manager.config["project_id"]
            url = f"{base_url}v1/general/projects/{project_id}/scan_profiles/{scanprofile_id}/scans/run"
            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}

            try:
                async with session.post(url, headers=headers) as response:
                    response.raise_for_status()
                    return response.status == 200
            except aiohttp.ClientResponseError as cre:
                print(f"HTTP error occurred: {cre.status}, message='{cre.message}', url={cre.request_info.url}")
                return False
            except Exception as e:
                print(f"An error occurred: {e}")
                return False
