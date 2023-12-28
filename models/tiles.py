#в базу не пишется, Тут будут ограничения на хотьбу и тд
import os
from PIL import Image, ImageFilter, ImageDraw

tiles_names = {
    0: 'water',
    1: 'grass',
    2: 'bush',
    3: 'stone'
}

tile_filenames = {
    0: os.path.join('tiles','water.png'),
    1: os.path.join('tiles','grass.png'),
    2: os.path.join('tiles','bush.png'),
    3: os.path.join('tiles','stone.png')
}

can_stay = ['grass']

class Tile:
    def __init__(self,id,x,y,_type):
        self.id = id
        self._type = _type
        self.name = tiles_names[_type]
        self.x = x
        self.y = y
        self.can_stay = self.name in can_stay
    
    def get_image(self):
        return Image.open(tile_filenames[self._type])

    