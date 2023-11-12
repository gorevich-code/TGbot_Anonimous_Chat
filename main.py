import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from handlers import start, stop, message


TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def main() -> None:
    """Main function: starts polling updates using start command, add data and get data routers"""

    dp.include_routers(start.router, stop.router, message.router,)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
