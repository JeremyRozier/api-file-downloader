import asyncio
from datetime import datetime
import os
import re
from typing import List
import aiohttp
from mainbot.bots.ent_bot import mainbot
from mainbot.constants import (
    URL,
    GWTPayload,
    HeExample2rs,
    RegexPatterns,
    TIMESTAMP_ID,
)
from mainbot.tools.timestamp_functions import (
    get_base64_from_datetime,
)


class Example2Bot(mainbot):
    """This class is a bot for Example2 website.
    It is meant to request Example2 API to get informations
    about objects such as their url.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        session_id=TIMESTAMP_ID,
        show_messages=False,
    ) -> None:
        super().__init__(session, username, password, show_messages)
        self.session_id = session_id
        self.gwt_payload = GWTPayload(self.session_id)
        self.is_logged_in_Example2 = False

    async def login_Example2(self, url_Example2_login=URL.Example2_LOGIN):
        """Method to get the session key and store it
        in the session_key attribute

        Returns (bool):
            - True if the operation succeeded.
            - False if the operation failed.
        """
        await self.session.get(url_Example2_login)
        login_resp_object = await self.session.post(
            URL.MY_SCHEDULE,
            data=self.gwt_payload.Example2_login(),
            heExample2rs=HeExample2rs.GWT_HEExample2RS,
        )
        self.is_logged_in_Example2 = (
            self.username in (await login_resp_object.read()).decode()
        )
        if self.is_logged_in_Example2:
            await self.session.post(
                URL.WEB_CLIENT,
                data=self.gwt_payload.load_project(),
                heExample2rs=HeExample2rs.GWT_HEExample2RS,
            )
        return self.is_logged_in_Example2

    async def login(
        self, login_url=URL.ENT_LOGIN, url_Example2_login=URL.Example2_LOGIN
    ) -> bool:
        """Method to login with the
        credentials given in the class attributes

        Args:
            - login_url (str): The url of the service hosting service.
            The login page of example service subservices is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        if not self.is_logged_in_ent:
            if await super().login(login_url):
                return await self.login_Example2(url_Example2_login)
            return False
        return await self.login_Example2(url_Example2_login)

    async def get_tree_from_name(self, name: str) -> List[str]:
        """Get the"""
        response_object = await self.session.post(
            URL.DIRECT_SCHEDULE,
            data=self.gwt_payload.tree_ids(name),
            heExample2rs=HeExample2rs.GWT_HEExample2RS,
        )
        response = bytes.decode(await response_object.read())
        list_datas_id_name = re.findall(RegexPatterns.data_ID, response)
        return list_datas_id_name

    async def get_info_id(self, info: int) -> str:
        return (await self.get_tree_from_name(f"S{info} position"))[-1]

    async def get_groups_from_info(
        self,
        info_number: int,
        info_id: str,
    ) -> list[str]:
        response_object = await self.session.post(
            URL.DIRECT_SCHEDULE,
            data=self.gwt_payload.children_from_info(info_id, info_number),
            heExample2rs=HeExample2rs.GWT_HEExample2RS,
        )
        response = bytes.decode(await response_object.read())
        list_groups_id_name = RegexPatterns.data_ID_NAME.findall(response)
        return list_groups_id_name

    async def get_schedule_url(
        self,
        data_id: str,
        beg_date: datetime,
        end_date: datetime,
    ) -> str:
        beg_base64 = get_base64_from_datetime(beg_date)
        end_base64 = get_base64_from_datetime(end_date)
        response_object = await self.session.post(
            URL.CORE_SCHEDULE,
            data=self.gwt_payload.schedule_url(
                data_id,
                beg_base64,
                end_base64,
            ),
            heExample2rs=HeExample2rs.GWT_HEExample2RS,
        )
        response = bytes.decode(await response_object.read())
        encoded_url = re.search(RegexPatterns.schedule_URL, response).group(1)
        url = re.sub(
            RegexPatterns.URL_HEX_VALUES,
            lambda match: chr(int(match.group(1), 16)),
            encoded_url,
        )
        return url


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
        Example2_bot = Example2Bot(
            session,
            username,
            password,
        )
        await Example2_bot.login()


if __name__ == "__main__":
    asyncio.run(main())
