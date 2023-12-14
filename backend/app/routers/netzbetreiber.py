from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy import exc
from datetime import datetime
from app import models, schemas, database, oauth
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Union, List, Any
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.config import Settings

router = APIRouter(prefix="/netzbetreiber", tags=["Netzbetreiber"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")

async def check_netzbetreiber_role(current_user: models.Nutzer) -> None:
    if current_user.rolle != models.Rolle.Netzbetreiber:
        logger.error(f"Zugriff verweigert: Nutzer {current_user.user_id} ist kein Netzbetreiber")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nur Netzbetreiber haben Zugriff auf diese Daten")

#tarif erstellen
@router.post("/tarife", response_model=schemas.TarifResponse, status_code=status.HTTP_201_CREATED)
async def create_tarif(tarif: schemas.TarifCreate, current_user: models.Nutzer = Depends(oauth.get_current_user), db: AsyncSession = Depends(database.get_db_async)):
    try:
        await check_netzbetreiber_role(current_user)
        new_tarif = models.Tarif(**tarif.dict())
        db.add(new_tarif)
        await db.commit()
        await db.refresh(new_tarif)
        return new_tarif
    except exc.IntegrityError as e:
        logger.error(f"Tarif konnte nicht erstellt werden: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tarif konnte nicht erstellt werden: {e}")

#tarif aktualisieren
@router.put("/tarife/{tarif_id}", response_model=schemas.TarifResponse)
async def update_tarif(tarif_id: int, tarif: schemas.TarifCreate, current_user: models.Nutzer = Depends(oauth.get_current_user), db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user)
    query = select(models.Tarif).where(models.Tarif.tarif_id == tarif_id)
    result = await db.execute(query)
    existing_tarif = result.scalar_one_or_none()

    if existing_tarif is None:
        raise HTTPException(status_code=404, detail=f"Tarif mit ID {tarif_id} nicht gefunden")

    for key, value in tarif.dict().items():
        setattr(existing_tarif, key, value)

    await db.commit()
    await db.refresh(existing_tarif)
    return existing_tarif

#tarif löschen
@router.delete("/tarife/{tarif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tarif(tarif_id: int, current_user: models.Nutzer = Depends(oauth.get_current_user), db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user)

    # Überprüfen, ob der Tarif existiert
    delete_stmt = select(models.Tarif).where(models.Tarif.tarif_id == tarif_id)
    result = await db.execute(delete_stmt)
    db_tarif = result.scalar_one_or_none()
    if db_tarif is None:
        raise HTTPException(status_code=404, detail="Tarif nicht gefunden")

    # Überprüfen, ob es mehr als einen Tarif in der Datenbank gibt
    count_stmt = select(func.count(models.Tarif.tarif_id))
    total_tarife = await db.execute(count_stmt)
    total_count = total_tarife.scalar_one()

    if total_count <= 1:
        raise HTTPException(status_code=403, detail="Mindestens ein Tarif muss im System vorhanden sein")

    # Löschen des Tarifs
    await db.delete(db_tarif)
    await db.commit()

#alle tarife abrufen
@router.get("/tarife", response_model=List[schemas.TarifResponse])
async def get_tarife(current_user: models.Nutzer = Depends(oauth.get_current_user), db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user or models.Rolle.Admin) 
    select_stmt = select(models.Tarif)
    result = await db.execute(select_stmt)
    tarife = result.scalars().all()
    return tarife