from sqlalchemy import Column, ForeignKey, BigInteger, String, INTEGER, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy import select

from models.base import Base

from .map import *

class Hero(Base):
    __tablename__ = "hero_table"
    pk = Column(INTEGER, primary_key=True)
    owner_id = Column(BigInteger, ForeignKey('user_table.pk',name='fk_hero_owner_id'), nullable=False)
    owner = relationship('User', backref='owner', lazy='subquery')

    avatar_file_id = Column(String(256), nullable=False)
    nick = Column(String(256), nullable=False)

    energy = Column(INTEGER, default=100)

    tile_id = Column(BigInteger, ForeignKey('map_table.pk',name='fk_tile_id'), nullable=True, default=0)
    tile = relationship('Map', backref='tile', lazy='subquery')

    async def init(self,session):
        if self.tile_id is None:
            await self.spawn(session)

        tmp = await session.execute(select(Map).where(Map.pk == self.tile_id))
        self.tile = tmp.scalar()
        self.x = self.tile.x
        self.y = self.tile.y

    def __repr__(self) -> str:
        tile = self.tile
        return f"{self.nick}, энергии {self.energy}, стоит в X:{tile.x},Y:{tile.y}"

    async def spawn(self,session):
        tile_id = await Map.get_random_tile_id_where_might_stay(session)
        self.tile_id = tile_id
        await session.commit()

    async def tp(self,session,cors):
        t = await Map.get_tile_by_cors(session,cors)
        self.tile_id = t.id
        await session.commit()

    async def add_hero(session, owner_id, avatar_file_id,nick=nick):
        
        hero = Hero(owner_id=owner_id, avatar_file_id=avatar_file_id,nick=nick,tile_id=1)
        session.add(hero)
        await hero.spawn(session)
        await session.commit()
        return hero.pk

    async def get_heroes_by_user(session, user):
        result = await session.execute(select(Hero).where(Hero.owner_id == user.pk))
        return result.scalars().all()

    async def get_hero_in_tile(session, tile):
        result = await session.execute(select(Hero).where(Hero.tile_id == tile.id))
        res = result.scalar()
        if res is None: return 0
        return res

    async def get_hero_by_id(session, id):
        result = await session.execute(select(Hero).where(Hero.pk == id))
        return result.scalar()
    
    async def check_neibg_tiles(self,session):
        await self.init(session)

        right = await Map.get_tile_by_cors(session,[self.x+1,self.y])
        left = await Map.get_tile_by_cors(session,[self.x-1,self.y])
        up = await Map.get_tile_by_cors(session,[self.x,self.y-1])
        down = await Map.get_tile_by_cors(session,[self.x,self.y+1])

        names = ['right','left','up','down']
        tiles = [right,left,up,down]
        free = []
        for t in tiles:
            another_hero = await Hero.get_hero_in_tile(session,t)
            free.append((not another_hero)*t.can_stay)
        
        return [num1 * num2 for num1, num2 in zip(free, names)]