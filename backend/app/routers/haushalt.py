from uuid import uuid4
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy import exc
from datetime import MAXYEAR, datetime, timedelta
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
from app.schemas import *
from app.models import *
import pandas as pd
import io
import re


router = APIRouter(prefix="/haushalt", tags=["Haushalt"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_haushalt_role(current_user: models.Nutzer, method: str, endpoint: str):
    if current_user.rolle != models.Rolle.Haushalte:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Haushalt",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Haushalte haben Zugriff auf diese Daten")
    
@router.post("/tarifantrag", response_model=VertragResponse)
async def erstelle_tarifantrag(antrag: TarifAntragCreate, current_user: models.Nutzer = Depends(oauth.get_current_user), db: AsyncSession = Depends(database.get_db_async)):

    haushalt = await db.get(models.Haushalt, current_user.user_id)
    if not haushalt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Haushalt nicht gefunden")

    neuer_vertrag = Vertrag(
        vertrag_id=str(uuid4()), 
        haushalt_id=current_user.user_id, 
        tarif_id=antrag.tarif_id,
        beginn_datum=date.today(),
        end_datum=datetime(MAXYEAR, 12, 31),
        jahresabschlag=100.0 
    )
    db.add(neuer_vertrag)
    await db.commit()
    await db.refresh(neuer_vertrag)
    return neuer_vertrag
