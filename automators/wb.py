import asyncio
import datetime
import os
import re
import traceback
from typing import Any
import aiohttp
import playwright
import playwright.async_api
from automators.controllers import DolphinController
from models.browser import BrowserContext, Page, Browser
from playwright.async_api import Page
from functools import wraps
import json
import random

DEFAULT_TIMEOUT = 60000 * 5


class WildberriesWorker(Browser):
    def __init__(self, headless: bool = False) -> None:
        super().__init__()
        self.headless = headless
        self.working: bool = True
        self.context = None
        self.users_page: dict[int, Page] = {}
        self.user_contexts: dict[int, BrowserContext] = {}

    """
    УВЫ, для этого сайта можно было просто просмотреть логи Fetch/XHR и вытащить внутренние API-запросы так и 
    быстрее и меньше шанс что случится проблема с XPATH до конкретного элемента
    """


if __name__ == "__main__":
    brow = WildberriesWorker()
    asyncio.run(brow.run())
