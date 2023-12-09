from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from t import db_pass

engine = create_async_engine(f"postgresql+asyncpg://tg_bot:{db_pass}@localhost/rpg_hero_bot")
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[str] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column()
    
    def __repr__(self) -> str:
        return f"User(id={self.id}"

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio

    asyncio.run(init_models())
