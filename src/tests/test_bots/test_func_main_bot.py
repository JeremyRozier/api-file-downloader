"""Functional tests for MainBot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from mainbot.bots import Example2Bot, mainbot
from mainbot.bots.Example1_bot import Example1Bot
from mainbot.constants import HeExample2rs

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
        bot = mainbot(session, USERNAME, PASSWORD)
        assert await bot.login()


@pytest.mark.asyncio
async def test_get_Example1_bot():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = mainbot(session, USERNAME, PASSWORD)
        Example1_bot = await bot.get_Example1_bot()

        assert isinstance(Example1_bot, Example1Bot)
        assert len(Example1_bot.session_key) > 0


@pytest.mark.asyncio
async def test_get_Example2_bot():
    async with aiohttp.ClientSession(
        heExample2rs=HeExample2rs.LOGIN_HEExample2RS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = mainbot(session, USERNAME, PASSWORD)
        Example2_bot = await bot.get_Example2_bot()

        assert isinstance(Example2_bot, Example2Bot)
        assert Example2_bot.is_logged_in_Example2
