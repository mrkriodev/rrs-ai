from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from typing import AsyncGenerator


#DATABASE_URL = f'{DB_ASYNC_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
DATABASE_URL = "postgresql+asyncpg://postgres:1111@127.0.0.1:5432/files"
Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_marker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)



class Files(Base):
    __tablename__ = "file"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_marker() as session:
        yield session

