from fusion_brain import api
from aiogram.types import BufferedInputFile

async def generate(message):
    #мб перетащить это в модель будет лучше

    await message.answer(f"Щас будет сгенерирован перс, ожитайте 🐁...")            
    hero_pic = await api.generate_from_bot(message.text)
    hero_file = BufferedInputFile(hero_pic,filename='hero_pic.jpg')
    return hero_file
    