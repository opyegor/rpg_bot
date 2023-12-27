from sqlalchemy import Column, ForeignKey, BigInteger, String, INTEGER, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy import select

from models.base import Base

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

    def __repr__(self) -> str:
        return f"{self.nick}, id владельца:{self.owner_id}, энергии {self.energy}"

    async def add_hero(session, owner_id, avatar_file_id,nick=nick):

        hero = Hero(owner_id=owner_id, avatar_file_id=avatar_file_id,nick=nick)
        session.add(hero)
        await session.commit()

    async def get_heroes_by_user(session, user):
        result = await session.execute(select(Hero).where(Hero.owner_id == user.pk))
        return result.scalars().all()
    