import aiohttp
from mainbot.constants import Payload, URL
from mainbot import bots


class MainBot:
    """This class is a bot for AMU website.
    It is meant to login to the ENT service so that
    it can be used in its subclasses to then access
    other services.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        show_messages=False,
    ) -> None:
        self.session = session
        self.username = username
        self.password = password
        self.show_messages = show_messages
        self.is_logged_in_ent = False

    async def login(self, login_url=URL.ENT_LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes

        Args:
            - login_url (str): The url of the service hosting service.
            The login page of example service subservices is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        async with self.session.post(
            login_url, data=Payload.login(self.username, self.password)
        ) as response:
            if (
                response.status == 401
                or len(self.password) == 0
                or len(self.username) == 0
            ):
                self.is_logged_in_ent = False
            else:
                self.is_logged_in_ent = True

        return self.is_logged_in_ent

    async def get_Example1_bot(
        self, url_Example1=URL.Example1
    ) -> "bots.Example1Bot":
        Example1_bot = bots.Example1Bot(
            self.session, self.username, self.password, show_messages=True
        )
        if self.is_logged_in_ent:
            await Example1_bot.load_Example1_session(url_Example1)
        else:
            await Example1_bot.login(url_Example1)
        return Example1_bot

    async def get_Example2_bot(
        self, url_Example2_login=URL.Example2_LOGIN
    ) -> "bots.Example2Bot":

        Example2_bot = bots.Example2Bot(
            self.session, self.username, self.password, show_messages=True
        )
        if self.is_logged_in_ent:
            await Example2_bot.login_Example2(url_Example2_login)
        else:
            await Example2_bot.login()
        return Example2_bot
