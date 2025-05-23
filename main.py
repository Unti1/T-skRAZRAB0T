
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault
from bot.middlewares.wb_clients_mid import WBClientsMiddleware
from settings.config import settings
from bot.handlers.product import r as basic_router

async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Запуск\Перезапуск бота')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    
async def main_bot_run():
    bot = Bot(
        token=settings.TELEGRAM_API,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(bot=bot)
    
    dp.include_routers(
        basic_router
    )

    wb_clients_mid = WBClientsMiddleware()
    dp.message.middleware(wb_clients_mid)
    dp.callback_query.middleware(wb_clients_mid)


    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main_bot_run())