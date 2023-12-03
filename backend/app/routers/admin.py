import sqlalchemy
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import exc, select
from app import models, schemas, database, config
from typing import List, Optional

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/logs", status_code=status.HTTP_200_OK, response_model=List[schemas.Log])
async def read_logs(
        start_datum: Optional[datetime] = None,
        end_datum: Optional[datetime] = None,
        user_id: Optional[int] = None,
        db: AsyncSession = Depends(database.get_db_async)
) -> List[schemas.Log]:
    """
    Asynchroner Endpunkt zum Abrufen von Protokolleinträgen aus der Datenbank.

    Parameter:
    - start_datum (datetime, optional): Der Startdatum zum Filtern von Protokollen.
    - end_datum (datetime, optional): Das Enddatum für die Filterung von Protokollen.
    - user_id (int, optional): Die Nutzer-ID zum Filtern von Protokollen.
    - db (AsyncSession): Die Abhängigkeit von der Datenbanksitzung.
K
    Returns:
    - List[schemas.Log]: Eine Liste von Protokolleinträgen, die den Filterkriterien entsprechen.

    Raises:
    - HTTPException 500 (Internal Server Error): Wenn ein Datenbankfehler auftritt
    """
    try:
        query = select(models.Log)
        if start_datum is not None:
            query = query.filter(models.Log.zeitpunkt >= start_datum)
        if end_datum is not None:
            query = query.filter(models.Log.zeitpunkt <= end_datum)
        if user_id is not None:
            query = query.filter(models.Log.user_id == user_id)

        result = await db.execute(query)
        logs = result.scalars().all()
        return logs
    except sqlalchemy.exc.SQLAlchemyError as e:
        detail = str(e) if config.settings.DEV else "Fehler beim Abrufen von Protokolldaten"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
