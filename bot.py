import asyncio
import logging
import sys
from io import BytesIO

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InputFile

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

from t import TOKEN
from texsts import *

from db import get_session
from models import *

from handlers import hero

class DataInput(StatesGroup):
    create_hero = State()
    set_nickname = State()
    travel_begin = State()
    travel_end = State()
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
async def command_help_handler(message):
    await message.answer(f'''{hbold(message.from_user.full_name)} {commands_help_text}''')

@dp.message(Command('create_hero'))
async def command_create_hero_handler(message, state):
    await create_hero_handler_start(message.from_user.id,state)

async def create_hero_handler_start(tg_id,state):    
    await state.clear()
    await bot.send_message(tg_id, 'Какого перса создать? Можешь описать несколько предложений, нейросеть создаст аватарку!')
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
        hero_id = await Hero.add_hero(session,user.pk,avatar_id,nick)
        await state.update_data(active_hero_id=hero_id)

    await message.answer("Герой создан! Отправляйся в приключения! /travel")
    await message.answer("Выбрать активного персонажа: /heroes")
    await state.clear()
    

@dp.message(Command('travel'))
async def travel(message, state):
    await travel_handler(message.from_user.id,message.chat.id,state)

async def travel_handler(tg_id,chat_id,state):
    state_data = await state.get_data()
    if await state.get_state() == DataInput.travel_begin:
        await bot.send_message(tg_id, 'Ты уже в путешествии!')
        return 0

    await state.set_state(DataInput.travel_begin)
    hero_id = state_data.get("active_hero_id")

    async for session in get_session():
        res = await hero.active_checker(hero_id,tg_id,session)
        if res is None:
            await create_hero_handler_start(tg_id,state)
            return 0
        hero_id = res
        await state.update_data(active_hero_id=hero_id)

    await bot.send_message(tg_id,'Топ топ...')
    async for session in get_session():
        h = await Hero.get_hero_by_id(session=session,id=hero_id)
        await h.init(session)

        map_file = await hero.generate_around(bot,session,h)
    
        sides = await h.check_neibg_tiles(session)

    builder = InlineKeyboardBuilder()
    if 'left' in sides:
        builder.button(text="\U00002B05", callback_data=f"go_left")
    else:
        builder.button(text="\U000026D4", callback_data=f"go_stop")

    if 'up' in sides:
        builder.button(text="\U00002B06", callback_data=f"go_up")
    else:
        builder.button(text="\U000026D4", callback_data=f"go_stop")

    if 'down' in sides:
        builder.button(text="\U00002B07", callback_data=f"go_down")
    else:
        builder.button(text="\U000026D4", callback_data=f"go_stop")

    if 'right' in sides:
        builder.button(text="\U000027A1", callback_data=f"go_right")
    else:
        builder.button(text="\U000026D4", callback_data=f"go_stop")

    await bot.send_photo(chat_id, photo=map_file,
                    caption=f'x:{h.x}, y:{h.y}', reply_markup=builder.as_markup())
    await state.set_state(DataInput.travel_end)
    await state.update_data(tg_id=tg_id)

@dp.callback_query(lambda c: c.data.startswith('go'))
async def process_group_buttons(callback_query: types.CallbackQuery, state):
    if await state.get_state() == DataInput.travel_begin:
        state_data = await state.get_data()
        tg_id = state_data.get("tg_id")
        await bot.send_message(tg_id, 'Ты уже в путешествии!')
        return 0
    else:
        direction = callback_query.data.split("_")[1]

        sides = {'left':[-1,0],'right':[1,0],'up':[0,-1],'down':[0,1],'stop':[0,0]}
        delta = sides[direction]

        state_data = await state.get_data()
        hero_id = state_data.get("active_hero_id")
        tg_id = state_data.get("tg_id")
        
        async for session in get_session():
            res = await hero.active_checker(hero_id,callback_query.message.from_user.id,session)
            if res is None:
                await command_start_handler(callback_query.message)
                return 0
            hero_id = res

        async for session in get_session():
            h = await Hero.get_hero_by_id(session,hero_id)
            await h.init(session)
            new_cors = [h.x + delta[0], h.y + delta[1]]
            await h.tp(session,new_cors)
        
        if direction != 'stop':
            await callback_query.answer(f"топ топ...")
            await travel_handler(tg_id, callback_query.message.chat.id, state)
        else:
            await callback_query.answer(f"куда прешь!")

        


@dp.message(Command('heroes'))
async def heroes(message, state):
    await state.set_state(DataInput.heroes)
    await state.update_data(tg_id=message.from_user.id)

    async for session in get_session():
        user = await User.get_user_by_tg(session,message.from_user.id)
        if user is None: 
            await command_help_handler(message)
            return 0
        else:
            heroes = await Hero.get_heroes_by_user(session,user)
            if len(heroes) == 0: 
                await command_create_hero_handler(message,state)
                return 0
            await message.answer("Выбирай кем играть:")
            for h in heroes:
                await h.init(session)
                if h.tile_id is None: await h.spawn(session)
                
                builder = InlineKeyboardBuilder()
                builder.button(text="Сделать активным", callback_data=f"hero {h.pk}")
                
                await bot.send_photo(message.chat.id, photo=h.avatar_file_id,
                                    caption=str(h), reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith('hero'))
async def process_group_buttons(callback_query: types.CallbackQuery, state):
   
    hero_pk = int(callback_query.data.split()[1])

    state_data = await state.get_data()
    tg_id = state_data.get("tg_id")

    async for session in get_session():
        h = await Hero.get_hero_by_id(session,hero_pk)

    await callback_query.answer(f"{h.nick} проставлен активным")
    await state.update_data(active_hero_id=h.pk)
    await travel_handler(tg_id,callback_query.message.chat.id, state)

async def main() -> None:
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())