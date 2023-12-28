from fusion_brain import api
from aiogram.types import BufferedInputFile

from models.map import Map
from models.user import User
from models.hero import Hero
from aiogram.types import InputFile

from PIL import Image, ImageFilter, ImageDraw
from aiogram.types import InputFile
import io
import base64
from io import BytesIO

async def active_checker(hero_id,tg_id,session):
    if hero_id is None:
        user = await User.get_user_by_tg(session,tg_id)
        heroes = await Hero.get_heroes_by_user(session,user)
        if len(heroes) == 0: 
            return None
        else:
            return heroes[0].pk
    return hero_id

async def generate(message):
    #мб перетащить это в модель будет лучше

    await message.answer(f"Щас будет сгенерирован перс, ожитайте 🐁...")            
    hero_pic = await api.generate_from_bot(message.text)
    hero_file = BufferedInputFile(hero_pic,filename='hero_pic.jpg')
    return hero_file
    
async def generate_around(bot,session,creature):
    width = 3
    height = 3
    
    cors = [creature.x, creature.y]

    final_image = Image.new('RGB', ((width*2+1)*32, (height*2+1)*32))
    x_n = 0
    for dx in range(-width,width+1):
        y_n = 0
        for dy in range(-height,height+1):
            tmp_cors = [cors[0]+dx,cors[1]+dy]
            tile = await Map.get_tile_by_cors(session=session, cors=tmp_cors)
            tile_image = tile.get_image()
            final_image.paste(tile_image, (x_n*32, y_n*32))

            another_hero = await Hero.get_hero_in_tile(session,tile)
            if another_hero:
                file = await bot.get_file(another_hero.avatar_file_id)

                my_object = BytesIO()
                another_hero.ava = await bot.download_file(file.file_path, my_object)
                h_img = Image.open(another_hero.ava)
                h_img = h_img.resize((32,32))
                final_image.paste(h_img, (x_n*32, y_n*32))

            if dx == 0 and dy == 0:
                file = await bot.get_file(creature.avatar_file_id)

                my_object = BytesIO()
                creature.ava = await bot.download_file(file.file_path, my_object)
                h_img = Image.open(creature.ava)
                h_img = h_img.resize((32,32))
                final_image.paste(h_img, (x_n*32, y_n*32))
            y_n += 1
        x_n += 1
    
    image_bytes = io.BytesIO()
    final_image.save(image_bytes, format='JPEG')
    input_file = BufferedInputFile(image_bytes.getvalue(),filename='map_pic.jpg')
    return input_file