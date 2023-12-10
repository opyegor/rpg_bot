import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from t import TOKEN

from db import get_session
from models import *
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    async for session in get_session():
        if not await User.check_tg_user_exist(session,message.from_user.id):
            await User.add_user(session,message.from_user.id)
            await message.answer(f"Ты добавлен в базу, {hbold(message.from_user.full_name)}!")
        else:
            await message.answer(f"Ты уже в базе, {hbold(message.from_user.full_name)}!")

async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())