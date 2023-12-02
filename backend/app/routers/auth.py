from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import exc
from sqlalchemy.future import select
from app import models, schemas, database, config

from app import schemas, database, models


router = APIRouter(prefix="/login", tags=["authentication"])


@router.post("/")
def login(user_creds: schemas.NutzerLogin, db: AsyncSession = Depends(database.get_db_async)):
    pass
