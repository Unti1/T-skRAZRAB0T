import asyncio
import logging
import traceback
from typing import Optional

import playwright
import psutil
import requests
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from settings.config import settings

from automators.controllers import DolphinController
from automators.controllers.NSTController import launch_and_return_browser_ws_endpoint
from schemas.account import AccountDataPD
from settings import config


class BaseBrowser:
    """Standart Browser Model for user action"""

    id_count = 0

    def __new__(cls, *args, **kwargs):
        cls.id_count += 1
        return super().__new__(cls)

    def __init__(self, *args, **kwargs) -> None:
        self.id = self.id_count
        print(f"[{self.__class__.__name__}] Worker emulator id:", self.id)

        self.browser: Browser = None
        self.playwright = None
        self.page: Optional[Page] = None
        self.headless = kwargs.get("headless", False)

        self.account_contexts: dict[str, BrowserContext] = {}
        self.account_page: dict[str, Page] = {}

        self.browser_model = ""
        self.brow_id = kwargs.get("brow_id", "")

    async def safe_evaluate(
        self, page: Page, script: str, data: dict = None, max_retries=5, delay=1
    ):
        retries = 0
        while retries < max_retries:
            try:
                result = await page.evaluate(script, data)
                return result
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logging.warning(
                    f"Попытка {retries + 1} из {max_retries} завершилась ошибкой: {e}\n{traceback.format_exc()}"
                )
                retries += 1
                await asyncio.sleep(delay)

        raise Exception("Операция не удалась после всех попыток")

    async def prepare_context(self, account: AccountDataPD):
        if account.id not in self.account_contexts:
            context: BrowserContext = await self.browser.new_context(
                viewport={
                    "width": settings.SCREEN_WIDTH,
                    "height": settings.SCREEN_HEIGHT,
                }
            )
        else:
            try:
                context: BrowserContext = self.account_contexts[account.id]
                try:
                    page = await context.new_page()
                    await page.close()
                except Exception as e:
                    print(f"Контекст закрыт: {e}")
                    self.account_contexts[account.id] = await self.browser.new_context(
                        viewport={
                            "width": settings.SCREEN_WIDTH,
                            "height": settings.SCREEN_HEIGHT,
                        }
                    )
                    context: BrowserContext = self.account_contexts[account.id]
            except playwright._impl._errors.TargetClosedError:
                context: BrowserContext = await self.browser.new_context(
                    viewport={
                        "width": settings.SCREEN_WIDTH,
                        "height": settings.SCREEN_HEIGHT,
                    }
                )

        print(f"Создан контекст для аккаунта {account.id}")
        return context

    async def _relaunch_browser(self, browser_model="", brow_id=""):
        try:
            await self.prepare_browser(
                browser_model=browser_model
                if browser_model != ""
                else self.browser_model,
                brow_id=brow_id if brow_id != "" else self.brow_id,
            )
        except requests.exceptions.ConnectionError as e:
            if (
                "HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url"
                in str(e)
            ):
                # requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /v1.0/browser_profiles/499247513/stop (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7ff950324f50>: Failed to establish a new connection: [Errno 111] Connection refused'))
                process = await asyncio.create_subprocess_shell(
                    "nohup ./dolphin-anty-linux-x86_64-latest.AppImage --no-sandbox",  # Команда
                    stdout=asyncio.subprocess.DEVNULL,  # Игнорируем стандартный вывод
                    stderr=asyncio.subprocess.DEVNULL,  # Игнорируем стандартный вывод ошибок
                )
                await asyncio.sleep(6)
                return await self._relaunch_browser(browser_model, brow_id)
            else:
                raise

    def proxy_config(
        self, host=None, port=None, login=None, password=None, proxy_type="https"
    ):
        if not (host and port):
            raise ValueError("Не переданы хост и порт прокси")

        match proxy_type:
            case "https":
                return {
                    "server": f"http://{host}:{port}",
                    "username": f"{login}",
                    "password": f"{password}",
                }
            case "socks5":
                return {
                    "server": f"socks5://{host}:{port}",
                    "username": f"{login}",
                    "password": f"{password}",
                }

    async def init_browser(self, proxy=False, **kwargs) -> None:
        """Инициализация браузера

        Args:
            proxy (bool, optional): Параметр для подключения прокси. По умолчанию False.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            proxy=self.proxy_config(**kwargs) if proxy else None,
        )
        self.page = await self.browser.new_page()

    async def create_page(
        self, account: AccountDataPD, base_url: str = "https://google.com"
    ):
        """Создание страницы в соотвествии с аккаунтом

        Args:
            account (_type_): Сама модель аккаунт
        """
        try:
            if not self.browser.is_connected():
                print("[WARNING] Браузер неактивен. Перезапуск...")
                await self._relaunch_browser()

            if account.id not in self.account_contexts:
                context: BrowserContext = await self.browser.new_context(
                    viewport={"width": settings.SCREEN_WIDTH, "height": settings.SCREEN_HEIGHT}
                )
            else:
                context: BrowserContext = self.account_contexts[account.id]

            page = await context.new_page()
            await page.goto(base_url)

            self.account_contexts[account.id] = context
            self.account_page[account.id] = page

            await self.account_page[account.id].reload()
        except Exception:
            print(
                f"[ERROR] Ошибка создания страницы для пользователя {account.id}: {traceback.format_exc()}"
            )
            raise

    async def close_browser(self) -> None:
        if self.browser:
            for context in self.browser.contexts:
                await context.close()
            self.account_contexts.clear()
            self.account_page.clear()

            if self.browser_model == "anty":
                session = requests.Session()
                await DolphinController.stop_automation(session, self.brow_id)
            else:
                await self.browser.close()

    async def prepare_browser(self, browser_model, brow_id=""):
        await self.init_browser()
        chromium = self.playwright.chromium
        match browser_model:
            case "anty":
                auth_token = DolphinController.authentication()
                session = requests.session()
                headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                }
                session.headers = headers

                await asyncio.to_thread(
                    DolphinController.stop_automation(
                        session,
                        profile_id=config["Dolphin"]["brow_id"]
                        if brow_id == ""
                        else brow_id,
                    )
                )  # Закрытие конкретного браузера

                await asyncio.sleep(2)

                automation_json = await asyncio.to_thread(
                    DolphinController.start_automation(
                        session,
                        profile_id=config["Dolphin"]["brow_id"]
                        if brow_id == ""
                        else brow_id,
                        headless=self.headless,
                    )
                )

                print(f"{automation_json=}")
                dolphin_port = automation_json["automation"]["port"]
                ws_endpoint = f"http://localhost:{dolphin_port}"

                self.browser = await chromium.connect_over_cdp(ws_endpoint)
            case "nst":
                ws_endpoint = await launch_and_return_browser_ws_endpoint(
                    config["NST"]["brow_id"]
                )
                self.browser = await chromium.connect_over_cdp(ws_endpoint)
            case _:
                print(
                    'Used standart browser. Try add argument browser_model as "anty" or "nst"'
                )

    async def run(self, browser_model="", brow_id=""):
        """Main running of browser model. First run and prepare

        Args:
            browser_model (str, optional): _description_. Defaults to ''.
        """
        self.browser_model = browser_model
        await self.prepare_browser(browser_model=browser_model, brow_id=brow_id)


def kill_playwright_node_processes():
    def is_chrome_present(process):
        """
        Checking 'chrome' in proc tree.
        """
        try:
            for child in process.children(recursive=True):
                if "chrome" in child.name().lower():
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return False

    """
    Killing node, whose dont have any chrome process.
    """
    for process in psutil.process_iter(["pid", "name"]):
        try:
            if process.info["name"] == "node":
                parent = psutil.Process(process.info["pid"])

                process_path = parent.exe().lower()
                if "vscode" in process_path:
                    # logger.info(
                    #     f"Skipping process (PID: {parent.pid}, Path: {process_path})"
                    # )
                    continue

                if not is_chrome_present(parent):
                    # logger.info(
                    #     f"Terminating orphaned node process (PID: {parent.pid}| Name: {process.info['name']})"
                    # )
                    parent.terminate()
                    parent.wait()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
