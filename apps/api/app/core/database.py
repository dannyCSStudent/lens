from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://lens_user:lens_pass@localhost:5432/lens"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session

