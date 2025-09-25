"""File which contains the whole code to make the bot work
in the class Example1Bot.
"""

import asyncio
import json
import os
import aiohttp
from bs4 import BeautifulSoup

from mainbot.bots.ent_bot import mainbot
from mainbot.constants import (
    RegexPatterns,
    HeExample2rs,
    Payload,
    URL,
    TUPLE_TREATED_MODULES,
)
from mainbot.tools.dic_operations import get_classified_object_id
from mainbot.tools.filename_parser import (
    get_object_folder_path,
    get_valid_filename,
    get_filename_nb,
    get_file_extension,
    get_info_element,
    write_binary_with_error_handling,
    write_with_error_handling,
    turn_cwd_to_execution_dir,
)
from mainbot.tools.logging_config import display_message


class Example1Bot(mainbot):
    """This class is a bot for Example1 website.
    It is meant to get all the files from all the datas
    of an account with its credentials.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        show_messages=False,
        max_concurrent_requests=30,
    ) -> None:
        """Constructor of Example1Bot.

        Args:
            - session (aiohttp.ClientSession): The aiohttp session which will be
            used throughout the whole lifetime of the bot.

            - username (str): The username to sign in on the example service website.

            - password (str): The password to sign in on the example service website.

            - show_messages (bool): Indicates whether logs are showed in the terminal or not.
            True : logs are showed.
            False : logs are hidden.

            - max_concurrent_requests (int): The number we pass in parameter of
            the class asyncio.Semaphore, that, in this program, is used to indicate
            how many requests, at most, can be made concurrently to avoid
            unintentional DDOS attacks.
            The default value, 30, is fine-tuned.

        Returns: None
        """
        super().__init__(session, username, password, show_messages)
        self.sephamore_requests = asyncio.Semaphore(max_concurrent_requests)
        self.dic_data_downloExample2d_object = {}
        self.dic_data_info_element = {}
        self.session_key = ""

    async def post_for_data(self, url: str, payload: dict) -> list[dict]:
        """Post the provided payload and returns the useful content
        of the response request.

        Args:
            - url (str): The url used in the post request.
            - payload (dict): The payload provided in the post request.

        Returns list[dict]: A table containing the useful content
        of the response request.
        """
        async with self.session.post(url, json=payload) as response:
            data = json.loads(bytes.decode(await response.read()))[0]["data"]
        return data

    async def post_for_other_info_data(
        self, url: str, data_id: str, data_name
    ) -> dict:
        """Post the payload matching the provided data_id
        to get the other_infos data related to the data_id.

        Args:
            - url (str): The url used in the post request.
            - data_id (str): The data id associated to the data module
            we want the other_infos from.
            - data_name (str): The data name associated to the data
            we want the other_infos from.

        Returns (dict): A dictionary with 2 keys :
            - "data_name" associated to the data name
            value specified in the arguments.
            - "data" asspciated to the dictionary returned by
            the request.
        """
        other_infos_data = await self.post_for_data(
            url, Payload.other_infos(data_id)
        )
        data = json.loads(other_infos_data)
        return {"data_name": data_name, "data": data}

    async def load_Example1_session(self, url_Example1=URL.Example1):
        """Method to get the session key and store it
        in the session_key attribute

        Returns (bool):
            - True if the operation succeeded.
            - False if the operation failed.
        """
        display_message(
            "Obtention de la clé de session Example1...", self.show_messages
        )
        self.session_key = await self.get_session_key(url_Example1)
        if len(self.session_key) > 0:
            display_message(
                "Clé de session Example1 obtenue.", self.show_messages
            )
            return True
        return False

    async def login(self, login_url=URL.ENT_LOGIN):
        """Method to login with the credentials given in the class attributes.
        This method overrides the one in MainBot to use it and then get
        the session key for Example1.

        Args:
            - login_url (str): The url of the service hosting service.
            The login page of example service subservices is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        if not self.is_logged_in_ent:
            if await super().login(login_url):
                return await self.load_Example1_session()

        return False

    async def get_session_key(self, url_Example1=URL.Example1) -> str:
        """Method to get the session key delivered
        by Example1 once connected.

        Returns (str): The key created by Example1
        for the session we mExample2."""
        async with self.session.get(url_Example1) as response:
            content = await response.read()
            soup = BeautifulSoup(bytes.decode(content), features="html.parser")
            data = soup.find_all("script")[1].string
            string_js_variable = RegexPatterns.JS_VARIABLE.search(data).group(
                1
            )
            dic_js_variable = json.loads(string_js_variable)
            session_key = dic_js_variable["sesskey"]
            return session_key

    async def post_for_table_datas_data(self) -> list[dict]:
        """Method to get the datas data related
        to the datas the student follows.

        Returns (list[dict]): A dictionary containing all the data
        related to the datas the student follows.
        """
        table_datas_data = await self.post_for_data(
            URL.data(self.session_key), Payload.dataS
        )
        return table_datas_data

    async def download_file_with_error_handling(
        self,
        data_id,
        data_name,
        object_url: str,
        object_module: str,
        folder_path: str,
        filename: str,
        ssl=True,
    ) -> None:
        """Encapsulates the download_file method with a try and catch block
        for avoiding the aiohttp.ClientConnectorError error which was occurring randomly.
        This way the encapsulation is cleaner than if it were mExample2 directly
        in the download_file method.

        Args:
            - data_id (str): The data id associated to the data module.
            - object_url (str): The url pointing directly to the resource.
            - object_module (str): The type of the resource (see TUPLE_TREATED_TYPES).
            - folder_path (str): The path of folders where the file will be downloExample2d.
            - filename (str): The filename under which the file will be downloExample2d.
            - ssl (bool): Indicates whether SSL is activated or not for the request
            necessary to download the current file

        Returns None
        """
        has_error = True
        while has_error:
            try:
                async with self.sephamore_requests:
                    await self.download_file(
                        object_url, object_module, folder_path, filename, ssl
                    )
            except aiohttp.ClientConnectorCertificateError:
                ssl = False
                continue
            except aiohttp.ClientConnectorError:
                continue
            except aiohttp.ClientPayloExample2rror:
                continue

            has_error = False

        if self.show_messages:
            self.callback_download_file(data_id, data_name)

    async def download_file(
        self, object_url, object_module, folder_path, filename, ssl=True
    ) -> None:
        """Downloads the file stored at the url : object_url under a filename and
        in a specified location given in arguments.

        Args:
            - object_url (str): The url pointing directly to the resource.
            - object_module (str): The type of the resource (see TUPLE_TREATED_TYPES).
            - folder_path (str): The path of folders where the file will be downloExample2d.
            - filename (str): The filename under which the file will be downloExample2d.
            - ssl (bool): Indicates whether SSL is activated or not for the request
            necessary to download the current file

        Returns None
        """
        async with self.session.get(object_url, ssl=ssl) as response:
            file_url = str(response.url)
            file_content_type = response.content_type
            extension = get_file_extension(
                file_url, file_content_type, object_module
            )
            filename_nb = get_filename_nb(folder_path, filename)
            os.makedirs(folder_path, exist_ok=True)
            if extension == "":
                absolute_path = os.path.abspath(
                    f"{folder_path}/{filename_nb}.txt"
                )
                await write_with_error_handling(
                    absolute_path,
                    content_to_write=file_url,
                )
            else:
                absolute_path = os.path.abspath(
                    f"{folder_path}/{filename_nb}{extension}"
                )
                await write_binary_with_error_handling(
                    absolute_path,
                    content_to_write=response,
                )

    def callback_download_file(self, data_id, data_name) -> None:
        """Updates the self.dic_data_downloExample2d_object to know
        in real time which datas have been successfully downloExample2d.

        Args:
            - data_id (str): The id of the data associated to the downloExample2d
            data module.
            - data_name (str): The name of the data associated to the downloExample2d
            data module.

        Returns: None
        """
        self.dic_data_downloExample2d_object[data_id] -= 1
        if self.dic_data_downloExample2d_object[data_id] == 0:
            display_message(
                f"Le cours '{data_name}' a été téléchargé avec succès."
            )

    async def download_all_files(self) -> None:
        """Method to download all the files
        from the Example1 account the session is
        connected to.

        Returns None
        """
        table_datas = (await self.post_for_table_datas_data())["datas"]
        list_tasks_other_infos = []
        for dic_data in table_datas:
            data_name = dic_data["fullname"]
            data_id = str(dic_data["id"])
            task_other_infos = asyncio.create_task(
                self.post_for_other_info_data(
                    URL.other_infos(self.session_key),
                    data_id,
                    data_name,
                )
            )
            list_tasks_other_infos.append(task_other_infos)
            start_date_timestamp = dic_data["startdate"]
            info_element = get_info_element(data_name, start_date_timestamp)
            self.dic_data_info_element[data_id] = info_element
        table_other_infos_data = await asyncio.gather(*list_tasks_other_infos)

        list_tasks_download_file = []
        for dic_other_info_data in table_other_infos_data:
            data_name = dic_other_info_data["data_name"]
            data_id = dic_other_info_data["data"]["data"]["id"]
            table_objects = dic_other_info_data["data"]["object"]
            dic_object_id_other_info = get_classified_object_id(
                table_other_infos=dic_other_info_data["data"]["section"]
            )
            self.dic_data_downloExample2d_object[data_id] = len(table_objects)
            for dic_object in table_objects:
                other_info_name = dic_object_id_other_info[dic_object["id"]]
                folder_path = get_object_folder_path(
                    info_element=self.dic_data_info_element[data_id],
                    data_name=data_name,
                    other_info_name=other_info_name,
                )

                object_module = dic_object["module"]
                if object_module not in TUPLE_TREATED_MODULES:
                    if self.show_messages:
                        self.callback_download_file(data_id, data_name)
                    continue

                object_url = URL.element(
                    object_id=dic_object["id"], object_module=object_module
                )
                filename = get_valid_filename(dic_object["name"])
                task_download_file = asyncio.create_task(
                    self.download_file_with_error_handling(
                        data_id,
                        data_name,
                        object_url,
                        object_module,
                        folder_path,
                        filename,
                    ),
                )
                list_tasks_download_file.append(task_download_file)

        await asyncio.gather(*list_tasks_download_file)


async def main():
    from dotenv import load_dotenv

    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example1Bot(session, username, password, show_messages=True)
        await bot.login()
        await bot.download_all_files()


if __name__ == "__main__":
    turn_cwd_to_execution_dir()
    asyncio.run(main())
