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
    set_nickname = State()
    travel = State()
    heroes = State()

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
    await state.clear()
    await bot.send_message(message.from_user.id, 'Какого перса создать? Можешь описать несколько предложений, нейросеть создаст аватарку!')
    await state.set_state(DataInput.create_hero)
        
@dp.message(DataInput.create_hero)
async def create_hero(message, state):
    hero_pic = await hero.generate(message)
    sent_photo = await message.answer_photo(photo=hero_pic)
    file_id = sent_photo.photo[-1].file_id
    await state.update_data(avatar_id=file_id)
    
    await message.answer("Жми /create_hero заново, если не нравится!")
    await message.answer("Или пиши ник персонажа:")

    await state.set_state(DataInput.set_nickname)

@dp.message(DataInput.set_nickname)
async def set_nickname(message, state):
    state_data = await state.get_data()

    nick = message.text
    avatar_id = state_data.get("avatar_id")
    async for session in get_session():
        user = await User.get_user_by_tg(session,message.from_user.id)
    
    #async for session in get_session():    
        await Hero.add_hero(session,user.pk,avatar_id,nick)

    await message.answer("Герой создан! Отправляйся в приключения! /travel")
    await message.answer("Выбрать активного персонажа: /heroes")
    await state.clear()
    
@dp.message(Command('travel'))
async def travel(message, state):
    await state.set_state(DataInput.travel)
    await message.answer("Тут будет карта и кнопки с шагами")

@dp.message(Command('heroes'))
async def heroes(message, state):
    await state.set_state(DataInput.heroes)
    async for session in get_session():
        user = await User.get_user_by_tg(session,message.from_user.id)
        heroes = await Hero.get_heroes_by_user(session,user)

    await message.answer("Тут все персы юзера, и будет кнопка с выбором активного")
    for h in heroes:
        await message.answer(str(h))
        await bot.send_photo(message.chat.id, photo=h.avatar_file_id,caption=str(h))

async def main() -> None:
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())