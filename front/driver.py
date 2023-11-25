from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

#DATABASE_URL = f'{DB_ASYNC_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
DATABASE_URL = "postgresql+asyncpg://postgres:1111@127.0.0.1:5432/files"
Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_marker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Files(Base):
    __tablename__ = "file"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    class_pred: Mapped[str] = mapped_column(String, nullable=True)
    special_code: Mapped[str] = mapped_column(String, nullable=True)
    probability: Mapped[str] = mapped_column(String, nullable=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_marker() as session:
        yield session


async def set_class_pred(video_id: int, new_class_pred: str, session: AsyncSession):
    try:
        # Query the database for the specific video record
        result = await session.execute(select(Files).filter(Files.id == video_id))
        file_record = result.scalar_one_or_none()

        if file_record is None:
            return {"error": "File not found"}

        # Update the quality field
        file_record.class_pred = new_class_pred

        # Commit the changes
        await session.commit()

        return {"message": "class_pred updated successfully"}

    except SQLAlchemyError as e:
        await session.rollback()
        return {"error": str(e)}
    
async def set_status(video_id: int, new_status: int, session: AsyncSession):
    try:
        # Query the database for the specific video record
        result = await session.execute(select(Files).filter(Files.id == video_id))
        file_record = result.scalar_one_or_none()

        if file_record is None:
            return {"error": "File not found"}

        # Update the quality field
        file_record.status = new_status

        # Commit the changes
        await session.commit()

        return {"message": "Status updated successfully"}

    except SQLAlchemyError as e:
        await session.rollback()
        return {"error": str(e)}
