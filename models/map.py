from sqlalchemy import Column, ForeignKey, BigInteger, String, INTEGER, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy import select
from random import randint

from models.base import Base
from .tiles import Tile

class Map(Base):
    __tablename__ = "map_table"
    pk = Column(INTEGER, primary_key=True)
    
    x = Column(INTEGER)
    y = Column(INTEGER)

    _type = Column(INTEGER)

    def __repr__(self) -> str:
        return f"tile #{self.pk} - x:{self.x},y:{self.y}, тип {tiles_names[self._type]}"

    async def add_tile(session, x, y,_type):
        m = Map(x=x, y=y,_type=_type)
        session.add(m)
        await session.commit()

    async def get_tile_by_cors(session,cors):
        x,y = cors
        from_db = await session.execute(select(Map).where(Map.x == x).where(Map.y == y))
        m = from_db.scalar()
        if m is None:
            return Tile(0,x,y,0)
        return Tile(m.pk,m.x,m.y,m._type)
    
    async def get_tile_by_id(session,id):
        from_db = await session.execute(select(Map).where(Map.pk == id))
        info = from_db.scalar()
        return Tile(id,info.x,info.y,info._type)

    async def get_random_tile_id_where_might_stay(session):
        tile_id = randint(0,100000)
        tile = await Map.get_tile_by_id(session,id=tile_id)
        while not tile.can_stay: 
            tile_id = randint(0,100000)
            tile = await Map.get_tile_by_id(session,id=tile_id)

        return tile_id