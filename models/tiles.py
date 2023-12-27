#в базу не пишется, Тут будут ограничения на хотьбу и тд

tiles_names = {
    0: 'water',
    1: 'grass',
    2: 'bush',
    3: 'stone'
}

class Tile:
    def __init__(self,map_obj):
        self.name = tiles_names[map_obj._type]
        self.x = map_obj.x
        self.y = map_obj.y
