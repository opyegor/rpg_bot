from sqlalchemy import Column, BigInteger, String, INTEGER, Boolean

from sqlalchemy import select

from models.base import Base

class User(Base):
    __tablename__ = "user_table"
    pk = Column(INTEGER, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    banned = Column(Boolean,default=False, nullable=False)
    
    def __repr__(self) -> str:
        return f"User(в базе:{self.pk}, id тг:{self.tg_id} {self.banned * 'ЗАБАНЕН'}"

    async def get_user_nickname(session,id):
        result = await session.execute(select(User).where(User.id==id))
        return result.scalars().all()

    async def add_user(session, tg_id):
        user = User(tg_id=tg_id)
        session.add(user)
        await session.commit()