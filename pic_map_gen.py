import numpy as np
import matplotlib.pyplot as plt
import random, os

import asyncio

from PIL import Image, ImageFilter, ImageDraw

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend

# Генерация начального состояния карты с произвольными тайлами
def generate_initial_map(width, height, prob_water, prob_land, prob_bush, prob_rock):
    init_map = np.zeros((width, height), dtype=int)
    for i in range(width):
        for j in range(height):
            rand_val = random.uniform(0, 1)
            if rand_val < prob_water:
                init_map[i][j] = 0  # вода
            elif rand_val < prob_water + prob_land:
                init_map[i][j] = 1  # земля
            elif rand_val < prob_water + prob_land + prob_bush:
                init_map[i][j] = 2  # кусты
            else:
                init_map[i][j] = 3  # камни
    return init_map

# Шаг эволюции по правилам клеточного автомата
def cellular_automata_step(map, width, height, prob_water):
    new_map = np.copy(map)
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            neighbors = [map[i-1, j-1], map[i-1, j], map[i-1, j+1],
                         map[i, j-1], map[i, j], map[i, j+1],
                         map[i+1, j-1], map[i+1, j], map[i+1, j+1]]
            
            water_neighbors = neighbors.count(0)
            if water_neighbors > 5:
                new_map[i, j] = 0  # преобразование в воду
            elif water_neighbors > 3:
                new_map[i, j] = 1  # преобразование в землю
            elif water_neighbors > 1:
                new_map[i, j] = 2  # преобразование в кусты
            else:
                new_map[i, j] = 3  # преобразование в камни
    return new_map

def fog(img):
    # Создаем новый полупрозрачный слой для тумана
    img = img.filter(ImageFilter.GaussianBlur(radius=10))
    fog_layer = Image.new('RGBA', img.size, (200, 200, 200, 150))

    # Создаем объект ImageDraw для рисования на слое тумана
    fog_draw = ImageDraw.Draw(fog_layer)

    # Рисуем несколько клубов дыма
    fog_draw.ellipse((50, 50, 100, 100), fill=(180, 180, 180, 100))
    fog_draw.ellipse((150, 80, 200, 130), fill=(180, 180, 180, 100))
    fog_draw.ellipse((250, 120, 300, 170), fill=(180, 180, 180, 100))

    # Комбинируем изображение с туманом
    img_with_fog = Image.alpha_composite(img.convert('RGBA'), fog_layer)
    return img_with_fog

tile_images = {
    0: os.path.join('tiles','water.png'),
    1: os.path.join('tiles','grass.png'),
    2: os.path.join('tiles','bush.png'),
    3: os.path.join('tiles','stone.png')
}

# Параметры для генерации карты
width = 1000
height = 1000
prob_water = 0.5
prob_land = 0.25
prob_bush = 0.125
prob_rock = 0.125
iterations = 1

# Генерация начального состояния карты
map_data = generate_initial_map(width, height, prob_water, prob_land, prob_bush, prob_rock)

# Эволюция клеточного автомата
for _ in range(iterations):
    map_data = cellular_automata_step(map_data, width, height, prob_water)


from models.map import Map
from db import get_session

async def generate_map():
    for x, line in enumerate(map_data):
        for y, value in enumerate(line):
            async for session in get_session():
                tmp = await Map.add_tile(session,x,y,value)

if __name__ == "__main__":
    print('генерация карты уже была')
    #asyncio.run(generate_map())

'''
(Все что ниже, уйдет в обработчики)
# Создаем пустое изображение для карты 
final_image = Image.new('RGB', (width*32, height*32))

for i in range(width):
    for j in range(height):
        tile_id = map_data[i][j]
        tile_image = Image.open(tile_images[tile_id])

        # Применяем фильтр размытия для создания эффекта "тумана"
        #if random.random() < 0.5:
        #    tile_image = fog(tile_image)

        final_image.paste(tile_image, (i*32, j*32))

# Отображение карты
plt.imshow(final_image)
plt.show()

#final_image.show()'''