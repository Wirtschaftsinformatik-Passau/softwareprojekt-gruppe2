from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy import exc
from datetime import datetime
from app import models, schemas, database, oauth, types
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Union, List, Any
from pydantic import ValidationError
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.config import Settings
from app.schemas import LoggingSchema
import pandas as pd
import io
import re


router = APIRouter(prefix="/energieberatende", tags=["Energieberatende"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_energieberatende_role(current_user: models.Nutzer, method: str, endpoint: str):
    if current_user.rolle != models.Rolle.Energieberatende:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Energieberatender",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Energieberatende haben Zugriff auf diese Daten")

@router.post("/rechnungen", response_model=schemas.RechnungResponse, status_code=status.HTTP_201_CREATED)
async def create_rechnung(rechnung: schemas.RechnungCreate, db: AsyncSession = Depends(database.get_db_async)):
    try:
        neue_rechnung = models.Rechnungen(**rechnung.dict())
        db.add(neue_rechnung)
        await db.commit()
        await db.refresh(neue_rechnung)
        return neue_rechnung
    except SQLAlchemyError as e:
        logger.error(f"Rechnung konnte nicht erstellt werden: {e}")
        raise HTTPException(status_code=500, detail=f"Rechnung konnte nicht erstellt werden: {e}")