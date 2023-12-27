from sqlalchemy import Column, ForeignKey, BigInteger, String, INTEGER, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy import select

from models.base import Base
from tiles import *

class Map(Base):
    __tablename__ = "map_table"
    pk = Column(INTEGER, primary_key=True)
    
    x = Column(INTEGER)
    y = Column(INTEGER)

    _type = Column(INTEGER)

    def __repr__(self) -> str:
        return f"tile #{self.pk} - x:{self.x},y:{self.y}, тип {tiles_names[self._type]}"

    def sync_add_tile(session,x, y,_type):
        m = Map(x=x, y=y,_type=_type)
        session.add(m)
        session.commit()

    async def add_tile(session, x, y,_type):
        m = Map(x=x, y=y,_type=_type)
        session.add(m)
        await session.commit()

    async def get_tile_by_cors(self,cors):
        x,y = cors
        from_db = await session.execute(select(Map).where(Map.x == x).where(Map.y == y))
        return Tile(from_db)
    
    async def get_tile_by_id(self,id):
        from_db = await session.execute(select(Map).where(Map.pk == id))
        return Tile(from_db)