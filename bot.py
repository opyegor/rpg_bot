import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

from t import TOKEN

from db import get_session
from models import *

from handlers import hero

class DataInput(StatesGroup):
    create_hero = State()

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    async for session in get_session():
        if not await User.check_tg_user_exist(session,message.from_user.id):
            await User.add_user(session,message.from_user.id)
            await message.answer(f"Привет, {hbold(message.from_user.full_name)}!")
        await command_help_handler(message)

@dp.message(Command('help'))
async def command_help_handler(message: Message):
    await message.answer(f"{hbold(message.from_user.full_name)}\n Жми /create_hero чтобы создать перса!")

@dp.message(Command('create_hero'))
async def command_create_hero_handler(message, state):
    await bot.send_message(message.from_user.id, 'Какого перса создать?')
    await state.set_state(DataInput.create_hero)
        
@dp.message(DataInput.create_hero)
async def create_hero(message, state):
    hero_pic = await hero.generate(message)
    await message.answer_photo(photo=hero_pic)
    await message.answer("Жми /create_hero заново, если не нравится!")
    await state.clear()

async def main() -> None:
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())