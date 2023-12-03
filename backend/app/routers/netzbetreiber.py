from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from app import models, schemas, database

router = APIRouter(prefix="/netzbetreiber", tags=["Netzbetreiber"])


class TarifConflictError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Tarif bereits vorhanden.")


class DatabaseError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


class TarifNotFoundError(HTTPException):
    def __init__(self, detail: str = "Tarif nicht gefunden"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class HaushaltNotFoundError(HTTPException):
    def __init__(self, detail: str = "Haushalt nicht gefunden"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class VertragConflictError(HTTPException):
    def __init__(self, detail: str = "Vertrag bereits vorhanden"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class SpecificDatabaseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


@router.post("/tarife/create", status_code=status.HTTP_201_CREATED,
             response_model=schemas.StromtarifResponse)
async def create_stromtarif(
        tarif: schemas.StromtarifCreate,
        db: AsyncSession = Depends(database.get_db_async)
) -> schemas.StromtarifResponse:
    """
    Asynchroner Endpunkt zur Erstellung eines neuen Stromtarifs.

    Parameter:
    - tarif (schemas.StromtarifCreate): Die Daten des zu erstellenden Stromtarifs.
    - db (AsyncSession): Abhängigkeit zur asynchronen Datenbanksitzung.

    Returns:
    - schemas.StromtarifResponse: Die Daten des erstellten Stromtarifs.

    Raises:
    - TarifConflictError: Bei Konflikten wie bereits existierendem Tarif.
    - DatabaseError: Bei allgemeinen Datenbankfehlern.
    """
    try:
        db_tarif = models.Stromtarif(**tarif.model_dump())
        db.add(db_tarif)
        await db.commit()
        await db.refresh(db_tarif)
        return db_tarif
    except exc.IntegrityError:
        raise TarifConflictError()
    except Exception:
        raise DatabaseError()


@router.post("/vertraege/create", status_code=status.HTTP_201_CREATED,
             response_model=schemas.VertragResponse)
async def create_vertrag(
        vertrag: schemas.VertragCreate,
        db: AsyncSession = Depends(database.get_db_async)
) -> schemas.VertragResponse:
    """
    Asynchroner Endpunkt zur Erstellung eines neuen Vertrags.

    Parameters:
    - vertrag (schemas.VertragCreate): Die Daten des zu erstellenden Vertrags.
    - db (AsyncSession): Abhängigkeit zur asynchronen Datenbanksitzung.

    Returns:
    - schemas.VertragResponse: Die Daten des erstellten Vertrags.

    Raises:
    - TarifNotFoundError: Wenn der Tarif nicht gefunden wird.
    - HaushaltNotFoundError: Wenn der Haushalt nicht gefunden wird.
    - VertragConflictError: Bei Konflikten bei der Erstellung des Vertrags.
    - DatabaseError: Für Datenbankfehler.
    """
    try:
        if not await db.get(models.Stromtarif, vertrag.tarif_id):
            raise TarifNotFoundError()
        if not await db.get(models.Nutzer, vertrag.haushalt_id):
            raise HaushaltNotFoundError()

        db_vertrag = models.Vertrag(**vertrag.model_dump())
        db.add(db_vertrag)
        await db.commit()
        await db.refresh(db_vertrag)
        return db_vertrag
    except exc.IntegrityError:
        raise VertragConflictError()
    except exc.SQLAlchemyError:
        raise DatabaseError()
