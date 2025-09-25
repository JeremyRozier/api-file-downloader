"""Functional tests for Example1Bot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from typeguard import check_type
from typing import List, Dict
from mainbot.bots import Example1Bot
from mainbot.constants import HeExample2rs, Payload, URL

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


@pytest.mark.asyncio
async def test_login():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example1Bot(session, USERNAME, PASSWORD)
        assert await bot.login()


@pytest.mark.asyncio
async def test_post_for_data():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example1Bot(session, USERNAME, PASSWORD)
        await bot.login()
        table_datas = (
            await bot.post_for_data(URL.data(bot.session_key), Payload.dataS)
        )["datas"]
        assert check_type(table_datas, List[Dict])


@pytest.mark.asyncio
async def test_post_for_table_datas_data():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = Example1Bot(session, USERNAME, PASSWORD)
        await bot.login()
        table_datas = (await bot.post_for_table_datas_data())["datas"]
        assert check_type(table_datas, List[Dict])


@pytest.mark.asyncio
async def test_post_for_other_info_data():
    pass


@pytest.mark.asyncio
async def test_download_file():
    pass


@pytest.mark.asyncio
async def test_callback_download_file():
    pass
