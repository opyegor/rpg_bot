from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import *

async def get_user_nickname(session,id):
    result = await session.execute(select(User).where(User.id==id))
    return result.scalars().all()


async def add_user(session, id, nickname):
    user = User(id=str(id), nickname=nickname)
    session.add(user)
    await session.commit()