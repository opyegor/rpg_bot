import numpy as np
import random

import asyncio

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
    async for session in get_session():
        for x, line in enumerate(map_data):
            for y, value in enumerate(line):
                await Map.add_tile(session,x,y,value)

if __name__ == "__main__":
    asyncio.run(generate_map())