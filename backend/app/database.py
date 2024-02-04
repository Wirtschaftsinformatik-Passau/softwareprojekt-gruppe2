from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import config


SQL_URL_async = (f"postgresql+asyncpg://{config.settings.POSTGRES_USER}:{config.settings.POSTGRES_PASSWORD}@"
                 f"{config.settings.POSTGRES_HOST}:{config.settings.POSTGRES_PORT}/{config.settings.POSTGRES_DB}")
SQL_URL = (f"postgresql://{config.settings.POSTGRES_USER}:{config.settings.POSTGRES_PASSWORD}@"
           f"{config.settings.POSTGRES_HOST}:{config.settings.POSTGRES_PORT}/{config.settings.POSTGRES_DB}")
non_async = False

if non_async:
    engine = create_engine(SQL_URL)
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
else:
   engine = create_async_engine(SQL_URL_async, echo=True)
   Base = declarative_base()
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine,
                               expire_on_commit=False, class_=AsyncSession)


def get_db():
    """
    Funktion zur Bereitstellung einer Datenbankverbindung für synchrone Operationen.

    Returns:
        Session: Eine SQLAlchemy-Sitzung, die für den Zugriff auf die Datenbank verwendet werden kann.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async():
    """
    Funktion zur Bereitstellung einer Datenbankverbindung für asynchrone Operationen.

    Returns:
        AsyncSession: Eine SQLAlchemy-Async-Sitzung, die für den asynchronen Zugriff auf die Datenbank verwendet werden kann.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()