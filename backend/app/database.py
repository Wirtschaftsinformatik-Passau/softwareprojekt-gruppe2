from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


SQL_URL_async = "postgresql+asyncpg://postgres:postgres@localhost:5432/tose_backend"
SQL_URL = "postgresql://root:secret@172.17.0.2:5432/tose_backend"
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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()