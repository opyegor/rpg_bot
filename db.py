from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import sessionmaker

from t import db_url

#чтобы создать сессии и движок

engine = create_async_engine(db_url)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session
