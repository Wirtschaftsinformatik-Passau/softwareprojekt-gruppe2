import traceback
from datetime import MAXYEAR, date, timedelta
from datetime import date, datetime
from uuid import uuid4
from typing import List, Union
import sqlalchemy
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Path, Query
from sqlalchemy import select, func, exc, update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from  pydantic_core._pydantic_core import ValidationError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import selectinload
from app import models, schemas, database, oauth, types
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.schemas import *
import csv
import io
from fastapi.responses import StreamingResponse

KWH_VERBRAUCH_JAHR = 1500

router = APIRouter(prefix="/haushalte", tags=["Haushalte"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_haushalt_role(current_user: models.Nutzer, method: str, endpoint: str):
    """
    Überprüft, ob der aktuelle Nutzer die Rolle "Haushalte" hat.

    Args:
        current_user (models.Nutzer): Der aktuelle Nutzer.
        method (str): Die HTTP-Methode.
        endpoint (str): Der Endpunkt der Anfrage.

    Raises:
        HTTPException: Wenn der Nutzer keine Berechtigung hat.
    """
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


async def check_haushalt_or_solarteur_role(current_user: models.Nutzer, method: str, endpoint: str): 
    """
    Überprüft, ob der aktuelle Nutzer die Rolle "Haushalte" oder "Solarteure" hat.

    Args:
        current_user (models.Nutzer): Der aktuelle Nutzer.
        method (str): Die HTTP-Methode.
        endpoint (str): Der Endpunkt der Anfrage.

    Raises:
        HTTPException: Wenn der Nutzer keine Berechtigung hat.
    """
    if current_user.rolle != models.Rolle.Haushalte and current_user.rolle != models.Rolle.Solarteure:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Haushalt",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Haushalte oder Solarteure haben Zugriff auf diese Daten")

async def check_haushalt_or_solarteur_role_or_berater(current_user: models.Nutzer, method: str, endpoint: str):
    """
    Überprüft, ob der aktuelle Nutzer die Rolle "Haushalte", "Solarteure" oder "Energieberatende" hat.

    Args:
        current_user (models.Nutzer): Der aktuelle Nutzer.
        method (str): Die HTTP-Methode.
        endpoint (str): Der Endpunkt der Anfrage.

    Raises:
        HTTPException: Wenn der Nutzer keine Berechtigung hat.
    """
    if current_user.rolle != models.Rolle.Haushalte and current_user.rolle != models.Rolle.Solarteure \
            and current_user.rolle != models.Rolle.Energieberatende:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Haushalt",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Haushalte oder Solarteure haben Zugriff auf diese Daten")

@router.post("/angebot-anfordern", status_code=status.HTTP_201_CREATED, response_model=schemas.PVAnforderungResponse)
async def pv_installationsangebot_anfordern(db: AsyncSession = Depends(database.get_db_async),
                                            current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Erstellt ein PV-Installationsangebot für den Haushalt.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        schemas.PVAnforderungResponse: Die Antwort auf die Anforderung des PV-Installationsangebots.
    """
    await check_haushalt_role(current_user, "POST", "/angebot-anfordern")
    try:
        stmt = (select(models.Nutzer.user_id, func.count(models.PVAnlage.anlage_id).label("anfragen_count"))
                .join(models.PVAnlage, models.Nutzer.user_id == models.PVAnlage.solarteur_id, isouter=True)
                .group_by(models.Nutzer.user_id)
                .order_by("anfragen_count")
                .where(models.Nutzer.rolle == models.Rolle.Solarteure))
        result = await db.execute(stmt)


        pv_anlage = models.PVAnlage(
            haushalt_id=current_user.user_id,
            prozess_status=models.ProzessStatus.AnfrageGestellt
        )

        db.add(pv_anlage)
        await db.commit()
        await db.refresh(pv_anlage)

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebot-anfordern",
            method="POST",
            message="PV-Installationsangebot erfolgreich angefordert",
            success=True
        )
        logger.info(logging_obj.dict())

        return schemas.PVAnforderungResponse(
            anlage_id=pv_anlage.anlage_id,
            prozess_status=pv_anlage.prozess_status,
        )

    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/admin/userOverview",
            method="GET",
            message=f"Internet Serverfehler: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internet Serverfehler")


@router.get("/angebot-anfordern", response_model=Union[List[schemas.PVAnlageHaushaltResponse], List])
async def get_pv_anlage(db: AsyncSession = Depends(database.get_db_async),
                        current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft Informationen über PV-Anlagen für den Haushalt ab.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        Union[List[schemas.PVAnlageHaushaltResponse], List]: Eine Liste von PV-Anlageninformationen oder eine leere Liste.
    """
    await check_haushalt_role(current_user, "GET", "/angebot-anfordern")
    try:
        stmt = select(models.PVAnlage).where(models.PVAnlage.haushalt_id == current_user.user_id)
        result = await db.execute(stmt)
        pv_anlagen = result.scalars().all()

        if not pv_anlagen:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/angebot-anfordern",
                method="GET",
                message="Keine PV-Anlage gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            return []

        response = [{
            "anlage_id": anlage.anlage_id,
            "haushalt_id": anlage.haushalt_id,
            "solarteur_id": anlage.solarteur_id,
            "prozess_status": anlage.prozess_status,
            "nvpruefung_status": anlage.nvpruefung_status if anlage.nvpruefung_status else "Noch nicht geprüft",
        } for anlage in pv_anlagen]

        return response

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebot-anfordern",
            method="GET",
            message=f"Internet Serverfehler: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internet Serverfehler")


@router.get("/vertrag-preview/{tarif_id}", response_model=schemas.VertragPreview)
async def get_tarifantrag(tarif_id: int, db: AsyncSession = Depends(database.get_db_async),
                          current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft eine Vorschau des Vertrags für einen bestimmten Tarif ab.

    Args:
        tarif_id (int): Die ID des Tarifs.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        schemas.VertragPreview: Eine Vorschau des Vertrags.
    """
    await check_haushalt_role(current_user, "GET", f"/tarifantrag/{tarif_id}")
    try:
        query = select(models.Tarif).where((models.Tarif.tarif_id == tarif_id) &
                                           (models.Tarif.active == True))
        result = await db.execute(query)
        tarif = result.scalar_one_or_none()
        if not tarif:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/vertrag-preview",
                method="GET",
                message="Tarif nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarif nicht gefunden")

    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/vertrag-preview",
            method="GET",
            message=f"Fehler beim Abrufen des Tarifs: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen des Tarifs")

    try:
        beginn_datum = date.today()
        end_datum = timedelta(days=int(365 * tarif.laufzeit)) + beginn_datum
        jahresabschlag = tarif.grundgebuehr + tarif.preis_kwh * KWH_VERBRAUCH_JAHR

        response = {"beginn_datum": beginn_datum,
                    "end_datum": end_datum,
                    "jahresabschlag": jahresabschlag
                    }

        return response

    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebotsueberpruefung",
            method="GET",
            message=f"Fehler bei der Vertragserstellung {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler bei der Vertragserstellung: {e}")


# haushalt sieht alle tarife und kann sich für einen entscheiden
@router.post("/tarifantrag/{tarif_id}", response_model=schemas.VertragResponse)
async def tarifantrag(tarif_id: int,
                      current_user: models.Nutzer = Depends(oauth.get_current_user),
                      db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt einen Tarifantrag für den Haushalt.

    Args:
        tarif_id (int): Die ID des ausgewählten Tarifs.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        schemas.VertragResponse: Die Antwort auf den Tarifantrag.
    """
    # Prüfen, ob der angeforderte Tarif existiert
    await check_haushalt_role(current_user, "POST", f"/tarifantrag/{tarif_id}")
    user_id = current_user.user_id
    try:
        query = select(models.Tarif).where((models.Tarif.tarif_id == tarif_id) & (models.Tarif.active == True))
        result = await db.execute(query)
        tarif = result.scalar_one_or_none()
        if not tarif:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/tarifantrag",
                method="POST",
                message="Tarif nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarif nicht gefunden")

    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/tarifantrag",
            method="POST",
            message=f"Fehler beim Abrufen des Tarifs: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen des Tarifs")

    beginn_datum = date.today()
    end_datum = timedelta(days=int(365 * tarif.laufzeit)) + beginn_datum
    jahresabschlag = tarif.grundgebuehr + tarif.preis_kwh * KWH_VERBRAUCH_JAHR

    try:
        vertrag = models.Vertrag(
            user_id=user_id,
            tarif_id=tarif_id,
            beginn_datum=beginn_datum,
            end_datum=end_datum,
            jahresabschlag=jahresabschlag,
            vertragstatus=models.Vertragsstatus.Laufend,
            netzbetreiber_id=tarif.netzbetreiber_id
        )
        db.add(vertrag)
        await db.commit()
        await db.refresh(vertrag)
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebotsueberpruefung",
            method="GET",
            message=f"Vertrag {vertrag.vertrag_id} erfolgreich erstellt für Nutzer ID {user_id}",
            success=True
        )
        logger.info(logging_obj.dict())
        return schemas.VertragResponse(
            vertrag_id=vertrag.vertrag_id,
            user_id=vertrag.user_id,
            tarif_id=vertrag.tarif_id,
            beginn_datum=vertrag.beginn_datum,
            end_datum=vertrag.end_datum,
            jahresabschlag=vertrag.jahresabschlag,
            vertragstatus=vertrag.vertragstatus
        )

    except sqlalchemy.exc.IntegrityError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=user_id,
            endpoint="/tarifantrag",
            method="POST",
            message=f"Tarif für user bereits vorhanden: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Tarif {tarif_id} für user {user_id}existiert für user bereits")


    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebotsueberpruefung",
            method="GET",
            message=f"Fehler bei der Vertragserstellung {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler bei der Vertragserstellung: {e}")


@router.post("/kontaktaufnahme-energieberatenden", status_code=status.HTTP_201_CREATED,
             response_model=schemas.EnergieausweisAnfrageResponse)
async def kontakt_aufnehmen_energieberatenden(anlage_id: int = Query(None, description="Anlage ID der PV Anlage",),
                                              db: AsyncSession = Depends(database.get_db_async),
                                              current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Nimmt Kontakt mit Energieberatenden für den Haushalt auf, um einen Energieausweis anzufordern.

    Args:
        anlage_id (int, optional): Die ID der PV-Anlage. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        schemas.EnergieausweisAnfrageResponse: Die Antwort auf die Energieausweis-Anfrage.
    """
    await check_haushalt_role(current_user, "POST", "/kontaktaufnahme-energieberatenden")

    try:
        neue_anfrage = models.Energieausweise(
            haushalt_id=current_user.user_id,
            ausweis_status=models.AusweisStatus.AnfrageGestellt
        )

        db.add(neue_anfrage)
        await db.commit()
        await db.refresh(neue_anfrage)

        anlagen = await db.execute(select(models.PVAnlage).where(models.PVAnlage.haushalt_id == current_user.user_id))
        anlagen = anlagen.scalars().all()

        for anlage in anlagen:
            anlage.energieausweis_id = neue_anfrage.energieausweis_id
            anlage.prozess_status = models.ProzessStatus.AusweisAngefordert

        await db.commit()

        if anlage_id and anlage_id not in [a.anlage_id for a in anlagen]:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/kontaktaufnahme-energieberatenden",
                method="POST",
                message=f"Anlage {anlage_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Anlage {anlage_id} nicht gefunden oder gehört nicht zum Haushalt")

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kontaktaufnahme-energieberatenden",
            method="POST",
            message=f"Energieausweis Anfrage {neue_anfrage.energieausweis_id} erfolgreich erstellt",
            success=True
        )
        logger.info(logging_obj.dict())

        return schemas.EnergieausweisAnfrageResponse(
            energieausweis_id=neue_anfrage.energieausweis_id,
            haushalt_id=current_user.user_id,
            ausweis_status=neue_anfrage.ausweis_status.value
        )

    except exc.IntegrityError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kontaktaufnahme-energieberatenden",
            method="POST",
            message=f"IntegrityError encountered: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=409, detail="Konflikt beim Erstellen der Energieausweis Anfrage")

    except Exception as e:

        if isinstance(e, HTTPException):
            raise e

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kontaktaufnahme-energieberatenden",
            method="POST",
            message=f"Unexpected error: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail="Interner Serverfehler")


@router.get("/angebotsueberpruefung", status_code=status.HTTP_200_OK, response_model=List[schemas.AngebotResponse])
async def ueberpruefung_angebote(current_user: models.Nutzer = Depends(oauth.get_current_user),
                                 db: AsyncSession = Depends(database.get_db_async)):
    """
    Überprüft die Angebote für den Haushalt und gibt eine Liste von Angeboten zurück.

    Args:
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        List[schemas.AngebotResponse]: Eine Liste von Angeboten oder eine leere Liste.
    """
    await check_haushalt_role(current_user, "GET", "/angebotsueberpruefung")
    try:
        stmt = select(models.Angebot).where(models.Angebot.anlage_id == models.PVAnlage.anlage_id,
                                            models.PVAnlage.haushalt_id == current_user.user_id)
        result = await db.execute(stmt)
        angebote = result.scalars().all()

        if not angebote:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/angebotsueberpruefung",
                method="GET",
                message=f"Keine Angebote für Haushalt {current_user.user_id} gefunden.",
                success=False
            )
            logger.error(logging_obj.dict())
            return []

        response_list = [schemas.AngebotResponse(
            angebot_id=angebot.angebot_id,
            anlage_id=angebot.anlage_id,
            kosten=angebot.kosten,
            angebotsstatus=angebot.angebotsstatus,
            created_at=angebot.created_at
        ) for angebot in angebote]

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebotsueberpruefung",
            method="GET",
            message=f"Angebote erfolgreich abgerufen für Haushalt {current_user.user_id}.",
            success=False
        )
        logger.info(logging_obj.dict())

        return response_list

    except sqlalchemy.exc.SQLAlchemyError as db_exc:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebotsueberpruefung",
            method="GET",
            message=f"Datenbankfehler für Haushalt: {current_user.user_id}: {db_exc}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Datenbankfehler bei der Abfrage von Angeboten")
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebotsueberpruefung",
            method="GET",
            message=f"Unerwarteter Fehler für Haushalt {current_user.user_id}: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unerwarteter Fehler bei der Abfrage von Angeboten")


@router.get("/all-tarife", response_model=List[schemas.TarifResponseAll])
async def get_all_tarife(db: AsyncSession = Depends(database.get_db_async),
                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft eine Liste aller verfügbarer Tarife ab.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        List[schemas.TarifResponseAll]: Eine Liste aller verfügbarer Tarife.
    """
    await check_haushalt_role(current_user, "GET", "/all-tarife")
    try:
        stmt = select(models.Tarif).where(models.Tarif.active == True)
        result = await db.execute(stmt)
        tarife = result.scalars().all()
        return tarife
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.get("/all-tarife/{tarif_id}", response_model=schemas.TarifHaushaltResponse)
async def get_all_tarife(tarif_id: int,
                         db: AsyncSession = Depends(database.get_db_async),
                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft einen Haushaltstarif anhand der Tarif-ID ab.

    Args:
        tarif_id (int): Die ID des Tarifs.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        schemas.TarifHaushaltResponse: Informationen zum Haushaltstarif.
    """
    await check_haushalt_role(current_user, "GET", f"/all-tarife/{tarif_id}")
    try:
        stmt = select(models.Tarif, models.Nutzer) \
            .join(models.Nutzer, models.Tarif.netzbetreiber_id == models.Nutzer.user_id) \
            .where(models.Tarif.tarif_id == tarif_id)
        result = await db.execute(stmt)
        tarife = result.all()
        response = {
            "vorname": tarife[0][1].vorname,
            "nachname": tarife[0][1].nachname,
            "email": tarife[0][1].email,
            "tarif_id": tarife[0][0].tarif_id,
            "tarifname": tarife[0][0].tarifname,
            "preis_kwh": tarife[0][0].preis_kwh,
            "grundgebuehr": tarife[0][0].grundgebuehr,
            "laufzeit": tarife[0][0].laufzeit,
            "spezielle_konditionen": tarife[0][0].spezielle_konditionen,
        }
        return response

    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"SQL Fehler: {e}")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error {e}")


@router.get("/vertraege", response_model=Union[List[schemas.VertragTarifResponse], List])
async def get_vertraege(db: AsyncSession = Depends(database.get_db_async),
                        current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft die Verträge des Haushalts ab.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        Union[List[schemas.VertragTarifResponse], List]: Eine Liste von Verträgen oder eine leere Liste.
    """
    await check_haushalt_role(current_user, "GET", "/vertraege")
    try:
        stmt = select(models.Vertrag, models.Tarif).join(models.Tarif, models.Vertrag.tarif_id == models.Tarif.tarif_id) \
            .where(models.Vertrag.user_id == current_user.user_id)
        result = await db.execute(stmt)
        vertraege = result.all()

        if not vertraege:
            return []

        response = [{
            "vertrag_id": vertrag.vertrag_id,
            "user_id": vertrag.user_id,
            "tarif_id": vertrag.tarif_id,
            "beginn_datum": vertrag.beginn_datum,
            "end_datum": vertrag.end_datum,
            "jahresabschlag": vertrag.jahresabschlag,
            "vertragstatus": vertrag.vertragstatus,
            "tarifname": tarif.tarifname,
            "preis_kwh": tarif.preis_kwh,
            "grundgebuehr": tarif.grundgebuehr,
            "laufzeit": tarif.laufzeit,
            "netzbetreiber_id": tarif.netzbetreiber_id,
            "spezielle_konditionen": tarif.spezielle_konditionen
        } for vertrag, tarif in vertraege]

        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.post("/datenfreigabe", status_code=status.HTTP_201_CREATED,
             response_model=schemas.HaushaltsDatenFreigabeResponse)
async def daten_freigabe(freigabe_daten: schemas.HaushaltsDatenFreigabe,
                         current_user: models.Nutzer = Depends(oauth.get_current_user),
                         db: AsyncSession = Depends(database.get_db_async)):
    """
    Aktualisiert die Haushaltsdatenfreigabe und Dashboard-Aggregationsdaten für den Haushalt.

    Args:
        freigabe_daten (schemas.HaushaltsDatenFreigabe): Die freigegebenen Haushaltsdaten.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        schemas.HaushaltsDatenFreigabeResponse: Die Antwort auf die Haushaltsdatenfreigabe.
    """
    await check_haushalt_role(current_user, "POST", "/datenfreigabe")
    user_id = current_user.user_id
    haushaltsdaten = await db.execute(select(models.Haushalte).where(models.Haushalte.user_id == user_id))
    haushalt = haushaltsdaten.scalars().first()
    if not haushalt:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/datenfreigabe",
            method="POST",
            message="Kein Haushaltsdatensatz gefunden",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kein Haushaltsdatensatz gefunden")
    try:
        dashboard_agg_result = await db.execute(
            select(
                func.sum(models.DashboardSmartMeterData.pv_erzeugung).label("gesamt_pv_erzeugung"),
                func.avg(models.DashboardSmartMeterData.soc).label("durchschnitt_soc"),
                func.sum(models.DashboardSmartMeterData.batterie_leistung).label("gesamt_batterie_leistung"),
                func.sum(models.DashboardSmartMeterData.last).label("gesamt_last")
            ).where(models.DashboardSmartMeterData.haushalt_id == current_user.user_id)
        )
        dashboard_agg_data = dashboard_agg_result.first()

        aggregated_data = schemas.DashboardAggregatedData(
            gesamt_pv_erzeugung=dashboard_agg_data.gesamt_pv_erzeugung,
            durchschnitt_soc=dashboard_agg_data.durchschnitt_soc,
            gesamt_batterie_leistung=dashboard_agg_data.gesamt_batterie_leistung,
            gesamt_last=dashboard_agg_data.gesamt_last
        )

    except ValidationError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/datenfreigabe",
            method="POST",
            message=f"Validierungsfehler: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Keine Dashboard Daten: {e}")

    try:        
        update_query = (
            update(models.Haushalte)
            .where(models.Haushalte.user_id == current_user.user_id)
            .values(**freigabe_daten.dict(), anfragestatus=True)
        )
        await db.execute(update_query)
        await db.commit()
        
        pv_anlagen = await db.execute(select(models.PVAnlage).where(models.PVAnlage.haushalt_id == current_user.user_id))
        pv_anlagen = pv_anlagen.all()
        if pv_anlagen:
            for pv in pv_anlagen:
                pv[0].prozess_status = models.ProzessStatus.DatenFreigegeben
                await db.commit()
                await db.refresh(pv[0])
    except SQLAlchemyError as e:
        await db.rollback()
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/datenfreigabe",
            method="POST",
            message=f"Fehler beim Aktualisieren der Haushaltsdaten: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Aktualisieren der Haushaltsdaten: {e}")

    logging_obj = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/datenfreigabe",
        method="POST",
        message="Haushaltsdaten und Dashboard-Daten erfolgreich freigegeben",
        success=True
    )
    logger.info(logging_obj.dict())

    return schemas.HaushaltsDatenFreigabeResponse(
        message="Haushaltsdaten und Dashboard-Daten erfolgreich freigegeben",
        haushaltsdaten=freigabe_daten,
        dashboard_daten=aggregated_data
    )


@router.get("/vertraege/{vertrag_id}", response_model=schemas.VertragTarifNBResponse)
async def get_vertrag(vertrag_id: int,
                      db: AsyncSession = Depends(database.get_db_async),
                      current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft einen bestimmten Vertrag des Haushalts ab.

    Args:
        vertrag_id (int): Die ID des Vertrags.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        schemas.VertragTarifNBResponse: Informationen zum Vertrag und dem zugehörigen Netzbetreiber.
    """
    await check_haushalt_role(current_user, "GET", f"/vertraege/{vertrag_id}")
    try:
        stmt = select(models.Vertrag, models.Tarif, models.Nutzer) \
            .join(models.Tarif, models.Vertrag.tarif_id == models.Tarif.tarif_id) \
            .join(models.Nutzer, models.Vertrag.netzbetreiber_id == models.Nutzer.user_id) \
            .where(models.Vertrag.vertrag_id == vertrag_id)
        result = await db.execute(stmt)
        vertrag = result.first()
        response = {
            "vertrag_id": vertrag[0].vertrag_id,
            "tarif_id": vertrag[0].tarif_id,
            "beginn_datum": vertrag[0].beginn_datum,
            "end_datum": vertrag[0].end_datum,
            "jahresabschlag": vertrag[0].jahresabschlag,
            "tarifname": vertrag[1].tarifname,
            "vertragstatus": vertrag[0].vertragstatus,
            "preis_kwh": vertrag[1].preis_kwh,
            "grundgebuehr": vertrag[1].grundgebuehr,
            "laufzeit": vertrag[1].laufzeit,
            "netzbetreiber_id": vertrag[1].netzbetreiber_id,
            "spezielle_konditionen": vertrag[1].spezielle_konditionen,
            "vorname": vertrag[2].vorname,
            "nachname": vertrag[2].nachname,
            "email": vertrag[2].email,
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.put("/vertrag-deaktivieren/{vertrag_id}", status_code=status.HTTP_200_OK)
async def deactivate_vertrag(vertrag_id: int,
                             db: AsyncSession = Depends(database.get_db_async),
                             current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Deaktiviert einen Vertrag und erstellt eine Kündigungsanfrage.

    Args:
        vertrag_id (int): Die ID des zu deaktivierenden Vertrags.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        dict: Eine Bestätigungsmeldung.
    """
    endpoint = f"/vertrag-deaktivieren/{vertrag_id}"
    await check_haushalt_role(current_user, "GET", endpoint)

    try:
        stmt = select(models.Vertrag).where(models.Vertrag.vertrag_id == vertrag_id)
        result = await db.execute(stmt)
        vertrag = result.first()[0]

        if vertrag.vertragstatus == models.Vertragsstatus.Gekuendigt or \
           vertrag.vertragstatus == models.Vertragsstatus.Gekuendigt_Unbestaetigt:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Vertrag {vertrag_id} ist bereits gekündigt oder Kündigung ist ausstehend")

        vertrag.vertragstatus = models.Vertragsstatus.Gekuendigt_Unbestaetigt

        kuendigungsanfrage = models.Kündigungsanfrage(
            vertrag_id=vertrag.vertrag_id,
            bestätigt=False
        )
        db.add(kuendigungsanfrage)

        await db.commit()
        return {"message": f"Kündigungsanfrage für Vertrag {vertrag_id} wurde erstellt"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/haushalt-daten/{haushalt_id}", response_model=schemas.HaushaltsDatenFreigabe)
async def get_haushalt_daten(haushalt_id: int,
                             db: AsyncSession = Depends(database.get_db_async),
                             current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft die freigegebenen Haushaltsdaten für einen bestimmten Haushalt ab.

    Args:
        haushalt_id (int): Die ID des Haushalts.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        schemas.HaushaltsDatenFreigabe: Freigegebene Haushaltsdaten.
    """
    await check_haushalt_or_solarteur_role_or_berater(
        current_user, "GET", f"/haushalt-daten/{haushalt_id}"
    )
    try:
        stmt = select(models.Haushalte).where(models.Haushalte.user_id == haushalt_id)
        result = await db.execute(stmt)
        haushalt = result.first()
        if not haushalt:
            logging_error = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/haushalt-daten/{haushalt_id}",
                method="GET",
                message=f"Keine Haushaltsdaten für Haushalt {haushalt_id} gefunden",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Keine Haushaltsdaten für Haushalt {haushalt_id} gefunden")
        haushalt = haushalt[0]
        if haushalt.anzahl_bewohner is None:
            logging_error = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/haushalt-daten/{haushalt_id}",
                method="GET",
                message=f"Haushaltsdaten für Haushalt {haushalt_id} wurden noch nicht freigegeben",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail=f"Haushaltsdaten für Haushalt {haushalt_id} wurden noch nicht freigegeben")

        return {
            "anzahl_bewohner": haushalt.anzahl_bewohner,
            "heizungsart": haushalt.heizungsart,
            "baujahr": haushalt.baujahr,
            "wohnflaeche": haushalt.wohnflaeche,
            "isolierungsqualitaet": haushalt.isolierungsqualitaet,
            "ausrichtung_dach": haushalt.ausrichtung_dach,
            "dachflaeche": haushalt.dachflaeche,
            "energieeffizienzklasse": haushalt.energieeffizienzklasse,
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.put("/haushalt-daten/{haushalt_id}", status_code=status.HTTP_200_OK)
async def update_haushalt_daten(haushalt_id: int,
                                current_user: models.Nutzer = Depends(oauth.get_current_user),
                                db: AsyncSession = Depends(database.get_db_async),
                                haushalt_daten: schemas.HaushaltsDatenFreigabe = Depends(get_haushalt_daten)):
    """
    Aktualisiert die Haushaltsdaten für einen bestimmten Haushalt.

    Args:
        haushalt_id (int): Die ID des Haushalts.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        haushalt_daten (schemas.HaushaltsDatenFreigabe): Die zu aktualisierenden Haushaltsdaten.

    Returns:
        dict: Eine Bestätigungsmeldung.
    """
    await check_haushalt_role(current_user, "PUT", f"/haushalt-daten/{haushalt_id}")
    
    try:
        stmt = select(models.Haushalte).where(models.Haushalte.user_id == haushalt_id)
        result = await db.execute(stmt)
        haushalt = result.first()[0]
        if not haushalt:
            logging_obj = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/haushalt-daten/{haushalt_id}",
                method="PUT",
                message=f"Keine Haushaltsdaten für Haushalt {haushalt_id} gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Keine Haushaltsdaten für Haushalt {haushalt_id} gefunden")
        haushalt.anzahl_bewohner = haushalt_daten.anzahl_bewohner
        haushalt.heizungsart = haushalt_daten.heizungsart
        haushalt.baujahr = haushalt_daten.baujahr
        haushalt.wohnflaeche = haushalt_daten.wohnflaeche
        haushalt.isolierungsqualitaet = haushalt_daten.isolierungsqualitaet
        haushalt.ausrichtung_dach = haushalt_daten.ausrichtung_dach
        haushalt.dachflaeche = haushalt_daten.dachflaeche
        haushalt.energieeffizienzklasse = haushalt_daten.energieeffizienzklasse
        await db.commit()
        await db.refresh(haushalt)
        return {"message": f"Haushaltsdaten für Haushalt {haushalt_id} erfolgreich aktualisiert"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.put("/angebot-akzeptieren/{anlage_id}", status_code=status.HTTP_200_OK)
async def angebot_annehmen(anlage_id: int = Path(..., description="Die ID der PV-Anlage", gt=0),
                           current_user: models.Nutzer = Depends(oauth.get_current_user),
                           db: AsyncSession = Depends(database.get_db_async)):
    """
    Nimmt ein Angebot für eine PV-Anlage an, indem der Prozessstatus auf 'AngebotAngenommen' geändert wird.

    Parameters:
    - anlage_id: int - Pfadparameter, der die ID der PV-Anlage darstellt.
    - current_user: Nutzer - Der aktuelle authentifizierte Benutzer, der über Dependency Injection ermittelt wird.
    - db: AsyncSession - Die Datenbanksitzung, die über Dependency Injection erhalten wird.

    Returns:
    - dict: Eine Meldung, die das Ergebnis des Vorgangs angibt.

    Raises:
    - HTTPException: Mit Statuscode 404, wenn die PV-Anlage nicht gefunden wird oder dem Benutzer nicht gehört.
    - HTTPException: Mit Statuscode 400, wenn das Angebot bereits angenommen wurde.
    - HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "PUT", f"/angebot-annehmen/{anlage_id}")

    pv_anlage = await db.get(models.PVAnlage, anlage_id)
    if not pv_anlage or pv_anlage.haushalt_id != current_user.user_id:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-akzeptieren/{anlage_id}",
            method="PUT",
            message=f"PV-Anlage {anlage_id} nicht gefunden oder gehört nicht zu Benutzer {current_user.user_id}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"PV-Anlage mit der ID {anlage_id} nicht gefunden "
                                   f"oder gehört nicht zum aktuellen Haushalt.")

    if pv_anlage.prozess_status == models.ProzessStatus.AngebotAngenommen:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-akzeptieren/{anlage_id}",
            method="PUT",
            message=f"Angebot für PV-Anlage {anlage_id} bereits angenommen",
            success=False
        )
        logger.error(logging_obj.dict())
        return {"message": f"Angebot für PV-Anlage {anlage_id} wurde bereits angenommen."}

    try:
        pv_anlage.prozess_status = models.ProzessStatus.AngebotAngenommen
        await db.commit()
        await db.refresh(pv_anlage)

        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-akzeptieren/{anlage_id}",
            method="PUT",
            message=f"Benutzer {current_user.user_id} hat Angebot für PV-Anlage {anlage_id} angenommen",
            success=True
        )
        logger.info(logging_obj.dict())

    except Exception as e:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-akzeptieren/{anlage_id}",
            method="PUT",
            message=f"Fehler bei der Angebotsannahme für PV-Anlage {anlage_id}: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")

    return {"message": f"Angebot für PV-Anlage {anlage_id} erfolgreich angenommen."}


@router.get("/angebote/{anlage_id}")
async def get_angebot(anlage_id: int,
                      current_user: models.Nutzer = Depends(oauth.get_current_user),
                      db: AsyncSession = Depends(database.get_db_async)):
    """
    Ruft ein Angebot für eine bestimmte PV-Anlage ab.

    Args:
        anlage_id (int): Die ID der PV-Anlage.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        list: Eine Liste von Angeboten für die angegebene PV-Anlage.
    """
    await check_haushalt_role(current_user, "GET", f"/angebote/{anlage_id}")
    try:
        stmt = select(models.Angebot, models.PVAnlage)\
            .join(models.PVAnlage, models.Angebot.anlage_id == models.PVAnlage.anlage_id)\
            .where(models.Angebot.anlage_id == anlage_id)
        result = await db.execute(stmt)
        angebote = result.all()
        if not angebote:
            logging_obj = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/angebote/{anlage_id}",
                method="GET",
                message=f"Angebot {anlage_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Angebot {anlage_id} nicht gefunden")

        return [{
            "angebot_id": angebot.angebot_id,
            "kosten": angebot.kosten,
            "modulanordnung": anlage.modulanordnung,   
            "modultyp": anlage.modultyp,
            "kapazitaet": anlage.kapazitaet,
            "installationsflaeche": anlage.installationsflaeche,
            "created_at": angebot.created_at,
        } for angebot, anlage in angebote]
    except Exception as e:

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")

@router.post("/kuendigungsanfrage/{vertrag_id}")
async def kuendigungsanfrage(
        vertrag_id: int,
        neuer_tarif_id: int = Query(None, description="Die ID des neuen Tarifs"),
        current_user: models.Nutzer = Depends(oauth.get_current_user),
        db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt eine Kündigungsanfrage für einen Vertrag.

    Args:
        vertrag_id (int): Die ID des zu kündigenden Vertrags.
        neuer_tarif_id (int, optional): Die ID des neuen Tarifs. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        dict: Eine Bestätigungsmeldung.
    """
    user_id = current_user.user_id

    # Überprüfe den bestehenden Vertrag
    query = select(models.Vertrag).where(
        and_(
            models.Vertrag.vertrag_id == vertrag_id,
            models.Vertrag.user_id == user_id
        )
    )
    bestehender_vertrag = await db.execute(query)
    vertrag = bestehender_vertrag.scalar_one_or_none()
    if not vertrag:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")

    # Überprüfe den Vertragsstatus
    if vertrag.vertragstatus == models.Vertragsstatus.Laufend:
        vertrag.vertragstatus = models.Vertragsstatus.Gekuendigt_Unbestaetigt
    elif vertrag.vertragstatus in [models.Vertragsstatus.Gekuendigt, models.Vertragsstatus.Gekuendigt_Unbestaetigt]:
        raise HTTPException(status_code=409, detail="Vertrag ist bereits gekündigt oder Kündigung ist ausstehend")

    # Erstelle eine Kündigungsanfrage
    kuendigungsanfrage = models.Kündigungsanfrage(
        vertrag_id=vertrag.vertrag_id,
        bestätigt=False,
        neuer_tarif_id=neuer_tarif_id if neuer_tarif_id else None
    )
    db.add(kuendigungsanfrage)
    await db.commit()

    return {"message": f"Kündigungsanfrage für Vertrag {vertrag_id} wurde erstellt"}


@router.put("/angebot-ablehnen/{anlage_id}", status_code=status.HTTP_200_OK)
async def angebot_ablehnen(anlage_id: int = Path(..., description="Die ID der PV-Anlage", gt=0),
                           current_user: models.Nutzer = Depends(oauth.get_current_user),
                           db: AsyncSession = Depends(database.get_db_async)):
    """
    Lehnt ein Angebot für eine PV-Anlage ab, indem der Prozessstatus auf 'AngebotAbgelehnt' geändert wird.
    Parameters:
    - anlage_id: int - Pfadparameter, der die ID der PV-Anlage darstellt.
    - current_user: Nutzer - Der aktuelle authentifizierte Benutzer, der über Dependency Injection ermittelt wird.
    - db: AsyncSession - Die Datenbanksitzung, die über Dependency Injection erhalten wird.
    Returns:
    - dict: Eine Meldung, die das Ergebnis des Vorgangs angibt.
    Raises:
    - HTTPException: Mit Statuscode 404, wenn die PV-Anlage nicht gefunden wird oder dem Benutzer nicht gehört.
    - HTTPException: Mit Statuscode 400, wenn das Angebot bereits abgelehnt oder angenommen wurde.
    - HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "PUT", f"/angebot-ablehnen/{anlage_id}")

    pv_anlage = await db.get(models.PVAnlage, anlage_id)
    if not pv_anlage or pv_anlage.haushalt_id != current_user.user_id:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-ablehnen/{anlage_id}",
            method="PUT",
            message=f"PV-Anlage {anlage_id} nicht gefunden oder gehört nicht zu Benutzer {current_user.user_id}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"PV-Anlage mit der ID {anlage_id} nicht gefunden "
                                   f"oder gehört nicht zum aktuellen Haushalt.")

    if pv_anlage.prozess_status in [models.ProzessStatus.AngebotAngenommen, models.ProzessStatus.AngebotAbgelehnt]:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-ablehnen/{anlage_id}",
            method="PUT",
            message=f"Angebot für PV-Anlage {anlage_id} kann nicht geändert werden, da es bereits angenommen "
                    f"oder abgelehnt wurde.",
            success=False
        )
        logger.error(logging_obj.dict())
        return {"message": f"Angebot kann nicht geändert werden, da es bereits angenommen oder abgelehnt wurde."}

    try:
        pv_anlage.prozess_status = models.ProzessStatus.AngebotAbgelehnt
        await db.commit()
        await db.refresh(pv_anlage)

        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-ablehnen/{anlage_id}",
            method="PUT",
            message=f"Benutzer {current_user.user_id} hat Angebot für PV-Anlage {anlage_id} abgelehnt",
            success=True
        )
        logger.info(logging_obj.dict())

    except Exception as e:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebot-ablehnen/{anlage_id}",
            method="PUT",
            message=f"Fehler bei der Angebotsannahme für PV-Anlage {anlage_id}: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")

    return {"message": f"Angebot für PV-Anlage {anlage_id} erfolgreich abgelehnt."}


@router.get("/rechnungen", response_model=List[schemas.RechnungResponse])
async def get_rechnungen(rolle: str = Query(None, description="Zahlungsteller oder Empfänger"),
                         current_user: models.Nutzer = Depends(oauth.get_current_user),
                         db: AsyncSession = Depends(database.get_db_async)):
    """
    Ruft eine Liste von Rechnungen basierend auf der Rolle des Nutzers ab (Zahlungsteller oder Empfänger).

    Args:
        rolle (str, optional): Die Rolle des Nutzers (Zahlungsteller oder Empfänger). Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        list: Eine Liste von Rechnungen, die den angegebenen Kriterien entsprechen.
    """
    try:
        if rolle not in ["steller", "empfaenger"]:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/rechnungen",
                method="GET",
                message="Ungültige Rolle",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungültige Rolle")

        if rolle == "steller":
            query = select(models.Rechnungen).where(models.Rechnungen.steller_id == current_user.user_id)
        else:
            query = select(models.Rechnungen).where(models.Rechnungen.empfaenger_id == current_user.user_id)

        result = await db.execute(query)
        rechnungen_list = result.scalars().all()

        if not rechnungen_list:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/rechnungen",
                method="GET",
                message="Keine Rechnungen für den Nutzer gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keine Rechnungen gefunden")

        return rechnungen_list

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/rechnungen",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der Rechnungen: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen der Rechnungen")

    except Exception as e:

        if isinstance(e, HTTPException):
            raise e

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/rechnungen",
            method="GET",
            message=f"Allgemeiner Fehler beim Abrufen der Rechnungen: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")

@router.get("/rechnungen/{rechnung_id}", response_model=schemas.RechnungResponse)
async def get_rechnung(rechnung_id: int,
                       current_user: models.Nutzer = Depends(oauth.get_current_user),
                       db: AsyncSession = Depends(database.get_db_async)):
    """
    Ruft eine einzelne Rechnung basierend auf ihrer ID ab.

    Args:
        rechnung_id (int): Die ID der Rechnung, die abgerufen werden soll.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        schemas.RechnungResponse: Informationen zur abgerufenen Rechnung.

    Raises:
        HTTPException: Wenn die Rechnung nicht gefunden wird oder dem Benutzer nicht gehört.
    """
    try:
        await check_haushalt_role(current_user, "GET", f"/rechnungen/{rechnung_id}")

        query = select(models.Rechnungen).where(
            and_(
                models.Rechnungen.rechnung_id == rechnung_id,
                models.Rechnungen.empfaenger_id == current_user.user_id
            )
        )
        result = await db.execute(query)
        rechnung = result.scalar_one_or_none()

        if not rechnung:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/rechnungen/{rechnung_id}",
                method="GET",
                message=f"Rechnung {rechnung_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rechnung {rechnung_id} nicht gefunden")

        return rechnung

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/rechnungen/{rechnung_id}",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der Rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen der Rechnung")

    except Exception as e:

        if isinstance(e, HTTPException):
            raise e

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/rechnungen/{rechnung_id}",
            method="GET",
            message=f"Allgemeiner Fehler beim Abrufen der Rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")


@router.put("/rechnungen/{rechnung_id}/bezahlen", status_code=status.HTTP_200_OK)
async def rechnung_bezahlen(rechnung_id: int,
                            current_user: models.Nutzer = Depends(oauth.get_current_user),
                            db: AsyncSession = Depends(database.get_db_async)):
    """
    Setzt den Zahlungsstatus einer Rechnung auf 'True' (bezahlt).
    Parameters:
    - rechnung_id: int - Pfadparameter, der die ID der Rechnung darstellt.
    - current_user: Nutzer - Der aktuelle authentifizierte Benutzer.
    - db: AsyncSession - Die Datenbanksitzung.
    Returns:
    - dict: Eine Meldung, die das Ergebnis des Vorgangs angibt.
    Raises:
    - HTTPException: Mit Statuscode 404, wenn die Rechnung nicht gefunden wird oder dem Benutzer nicht gehört.
    - HTTPException: Mit Statuscode 400, wenn die Rechnung bereits bezahlt wurde.
    - HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "PUT", f"/rechnungen/{rechnung_id}/bezahlen")

    try:
        stmt = select(models.Rechnungen).where(
            (models.Rechnungen.rechnung_id == rechnung_id) & 
            (models.Rechnungen.empfaenger_id == current_user.user_id))
        result = await db.execute(stmt)
        rechnung = result.scalar_one_or_none()

        if not rechnung:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Rechnung nicht gefunden oder gehört nicht zum Nutzer")

        if rechnung.zahlungsstatus == models.Zahlungsstatus.Bezahlt:
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail="Rechnung bereits bezahlt")

        rechnung.zahlungsstatus = models.Zahlungsstatus.Bezahlt
        await db.commit()
        
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/rechnungen/{rechnung_id}/bezahlen",
            method="PUT",
            message="Rechnung erfolgreich als bezahlt markiert",
            success=True
        )
        logger.info(logging_obj.dict())

        return {"message": "Rechnung erfolgreich als bezahlt markiert"}

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/rechnungen/{rechnung_id}/bezahlen",
            method="PUT",
            message=f"Fehler beim Aktualisieren der Rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Fehler beim Aktualisieren der Rechnung")


@router.get("/download_reports_dashboard", status_code=status.HTTP_200_OK)
async def download_reports_dashbaord(db: AsyncSession = Depends(database.get_db_async),
                                current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Generiert einen Bericht über das Dashboard und ermöglicht den Download als CSV-Datei.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        StreamingResponse: Die CSV-Datei als Download.

    Raises:
        HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "GET", "/download_reports_dashboard")
    try:
        # Anzahl der laufenden PV-Anträge
        pv_anfragen_count = await db.execute(
            select(func.count(models.PVAnlage.anlage_id)).where(models.PVAnlage.prozess_status == "AnfrageGestellt")
        )

        # Anzahl der laufenden Verträge für den Haushalt
        vertraege_count = await db.execute(
            select(func.count(models.Vertrag.vertrag_id)).where(models.Vertrag.user_id == current_user.user_id)
        )

        # Erstellen der CSV-Datei
        output = io.StringIO()
        writer = csv.writer(output)

        # Schreiben der Kopfzeilen
        header = ["Kategorie", "Anzahl"]
        writer.writerow(header)

        # Schreiben der Daten
        writer.writerow(["Anzahl der laufenden PV-Anträge", pv_anfragen_count.scalar()])
        writer.writerow(["Anzahl der laufenden Verträge", vertraege_count.scalar()])

        output.seek(0)  # Zurück zum Anfang der Datei
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=haushalt_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)
    

@router.get("/download_reports_rechnungen", status_code=status.HTTP_200_OK)
async def download_reports_rechnungen(db: AsyncSession = Depends(database.get_db_async),
                           current_user: models.Nutzer = Depends(oauth.get_current_user)):

    """
    Generiert einen Bericht über Rechnungen und ermöglicht den Download als CSV-Datei.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        StreamingResponse: Die CSV-Datei als Download.

    Raises:
        HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "GET", "/download_reports_rechnungen")
    
    try:
        # Wählen Sie nur Rechnungen aus, die dem aktuellen Nutzer zugeordnet sind
        rechnungen = await db.execute(
            select(models.Rechnungen).where(models.Rechnungen.empfaenger_id == current_user.user_id)
        )

        # Erstellen der CSV-Datei
        output = io.StringIO()
        writer = csv.writer(output)

        # Schreiben der Kopfzeilen entsprechend der Tabelle Rechnungen
        header = [
            "rechnung_id", "empfaenger_id", "steller_id", "rechnungsbetrag", "rechnungsdatum",
            "faelligkeitsdatum", "rechnungsart", "zahlungsstatus", "rechnungsperiode_start", "rechnungsperiode_ende"
        ]
        writer.writerow(header)

        # Schreiben der Daten aus der Rechnungen-Tabelle
        for rechnung in rechnungen.scalars().all():
            writer.writerow([
                rechnung.rechnung_id,
                rechnung.empfaenger_id,
                rechnung.steller_id,
                float(rechnung.rechnungsbetrag),
                rechnung.rechnungsdatum.isoformat() if rechnung.rechnungsdatum else None,
                rechnung.faelligkeitsdatum.isoformat() if rechnung.faelligkeitsdatum else None,
                rechnung.rechnungsart.value if rechnung.rechnungsart else None,  # Enum-Wert
                rechnung.zahlungsstatus.value if rechnung.zahlungsstatus else None,  # Enum-Wert
                rechnung.rechnungsperiode_start.isoformat() if rechnung.rechnungsperiode_start else None,
                rechnung.rechnungsperiode_ende.isoformat() if rechnung.rechnungsperiode_ende else None,
            ])

        output.seek(0)  # Zurück zum Anfang der Datei
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=haushalt_rechnungen_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)


@router.get("/download_reports_vertrag", status_code=status.HTTP_200_OK)
async def download_reports_vertrag(db: AsyncSession = Depends(database.get_db_async),
                           current_user: models.Nutzer = Depends(oauth.get_current_user)):

    """
    Generiert einen Bericht über Verträge und ermöglicht den Download als CSV-Datei.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        StreamingResponse: Die CSV-Datei als Download.

    Raises:
        HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "GET", "/download_reports_vertrag")

    try:
        # Selektiere nur Verträge, die dem aktuellen Nutzer zugeordnet sind
        vertraege = await db.execute(
            select(models.Vertrag).where(models.Vertrag.user_id == current_user.user_id)
        )

        # Erstellen der CSV-Datei
        output = io.StringIO()
        writer = csv.writer(output)

        # Schreiben der Kopfzeilen entsprechend der Tabelle Vertrag
        header = [
            "vertrag_id", "user_id", "tarif_id", "beginn_datum", "end_datum",
            "netzbetreiber_id", "jahresabschlag", "vertragstatus"
        ]
        writer.writerow(header)

        # Schreiben der Daten aus der Vertrag-Tabelle
        for vertrag in vertraege.scalars().all():
            writer.writerow([
                vertrag.vertrag_id,
                vertrag.user_id,
                vertrag.tarif_id,
                vertrag.beginn_datum.isoformat() if vertrag.beginn_datum else None,
                vertrag.end_datum.isoformat() if vertrag.end_datum else None,
                vertrag.netzbetreiber_id,
                vertrag.jahresabschlag,
                vertrag.vertragstatus.value  
            ])

        output.seek(0)  # Zurück zum Anfang der Datei
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=haushalt_vertrag_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)
    

@router.get("/download_reports_energieausweise", status_code=status.HTTP_200_OK)
async def download_reports_eausweis(db: AsyncSession = Depends(database.get_db_async),
                           current_user: models.Nutzer = Depends(oauth.get_current_user)):

    """
    Generiert einen Bericht über Energieausweise und ermöglicht den Download als CSV-Datei.

    Args:
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.

    Returns:
        StreamingResponse: Die CSV-Datei als Download.

    Raises:
        HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_haushalt_role(current_user, "GET", "/download_reports_energieausweise")
    
    try:
        # Wählen Sie nur Energieausweise aus, die dem aktuellen Nutzer zugeordnet sind
        energieausweise = await db.execute(
            select(models.Energieausweise).where(models.Energieausweise.haushalt_id == current_user.user_id)
        )

        # Erstellen der CSV-Datei
        output = io.StringIO()
        writer = csv.writer(output)

        # Schreiben der Kopfzeilen entsprechend der Tabelle Energieausweise
        header = [
            "energieausweis_id", "haushalt_id", "massnahmen_id", "energieberater_id",
            "energieeffizienzklasse", "verbrauchskennwerte", "ausstellungsdatum", "gueltigkeit",
            "ausweis_status"
        ]
        writer.writerow(header)

        # Schreiben der Daten aus der Energieausweise-Tabelle
        for ausweis in energieausweise.scalars().all():
            writer.writerow([
                ausweis.energieausweis_id,
                ausweis.haushalt_id,
                ausweis.massnahmen_id,
                ausweis.energieberater_id,
                ausweis.energieeffizienzklasse,
                ausweis.verbrauchskennwerte,
                ausweis.ausstellungsdatum.isoformat() if ausweis.ausstellungsdatum else None,
                ausweis.gueltigkeit.isoformat() if ausweis.gueltigkeit else None,
                ausweis.ausweis_status.value  # Enum-Wert
            ])

        output.seek(0)  # Zurück zum Anfang der Datei
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=haushalt_energieausweise_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)