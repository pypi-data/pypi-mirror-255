import os

import aiofiles
import aiohttp
import platformdirs
import tomlkit


class Credentials:
    def __init__(self, access_token=None, refresh_token=None) -> None:
        self.__access_token = access_token
        self.__refresh_token = refresh_token
        self.__credentials_path = (
            platformdirs.user_config_dir("hacktegic", ensure_exists=True)
            + "/credentials"
        )

    async def authenticated(self) -> bool:
        """
        Checks if the user is authenticated

        :return: A boolean indicating whether the user is authenticated or not.
        """
        if not self.__access_token:
            return False

        from hacktegic._internal.config import ConfigManager

        config_manager = ConfigManager()
        await config_manager.load()

        async with aiohttp.ClientSession() as session:
            url = f'{config_manager.config["api_base_url"]}v1/general/me'
            headers = {"Authorization": f"Bearer {self.__access_token}"}

            async with session.get(url, headers=headers) as response:
                return response.status == 200

    async def refresh(self) -> None:
        pass

    async def revoke(self) -> None:
        pass

    async def save(self) -> None:
        """
        Save the credentials to file.
        """
        doc = tomlkit.document()
        hacktegic = doc["hacktegic"] = tomlkit.table()
        hacktegic["access_token"] = self.__access_token
        hacktegic["refresh_token"] = self.__refresh_token
        async with aiofiles.open(self.__credentials_path, mode="w") as f:
            content = tomlkit.dumps(doc)
            await f.write(content)

    async def load(self) -> None:
        """
        Load the credentials from file.
        """
        if not os.path.exists(self.__credentials_path):
            return
        async with aiofiles.open(self.__credentials_path, mode="r") as f:
            doc = tomlkit.loads(await f.read())
            self.__access_token = doc["hacktegic"]["access_token"]
            self.__refresh_token = doc["hacktegic"]["refresh_token"]

    async def remove(self) -> bool:
        try:
            if os.path.exists(self.__credentials_path):
                os.remove(self.__credentials_path)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error occurred while removing credentials file: {e}")
            return False

    @property
    def access_token(self) -> str:
        return self.__access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        self.__access_token = value

    @property
    def refresh_token(self) -> str:
        return self.__refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str) -> None:
        self.__refresh_token = value
