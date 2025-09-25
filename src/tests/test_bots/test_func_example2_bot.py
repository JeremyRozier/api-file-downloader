"""Functional tests for Example1Bot class"""

from datetime import datetime
import os
import aiohttp
from dotenv import load_dotenv
import pytest
from mainbot.bots import mainbot, Example2Bot
from mainbot.constants import HeExample2rs


load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


@pytest.mark.asyncio
async def test_login_Example2():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example2Bot(session, USERNAME, PASSWORD)
        assert not await bot.login_Example2()
        ent_bot = mainbot(session, USERNAME, PASSWORD)
        assert await ent_bot.login()
        Example2_bot = Example2Bot(session, USERNAME, PASSWORD)
        assert await Example2_bot.login_Example2()


@pytest.mark.asyncio
async def test_login():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example2Bot(session, USERNAME, PASSWORD)
        assert await bot.login()


@pytest.mark.asyncio
async def test_get_tree_ids_from_name():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example2Bot(session, USERNAME, PASSWORD)
        await bot.login()
        list_datas_id = "Example"
        assert list_datas_id == [
            "-100",
            "-1",
            "686",
            "13105",
            "706",
            "13114",
            "1823",
            "1915",
        ]


@pytest.mark.asyncio
async def test_get_info_id():
    pass


@pytest.mark.asyncio
async def test_get_groups_from_info():
    pass


@pytest.mark.asyncio
async def test_get_schedule_url():
    pass
