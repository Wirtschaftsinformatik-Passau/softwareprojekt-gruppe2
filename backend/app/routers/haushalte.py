from datetime import MAXYEAR, date, timedelta
from datetime import date, datetime
from uuid import uuid4
from typing import List

import sqlalchemy
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy import select, func, exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas, database, oauth, types
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.schemas import LoggingSchema, TarifAntragCreate, VertragResponse

KWH_VERBRAUCH_JAHR = 1500

router = APIRouter(prefix="/haushalte", tags=["Haushalte"])

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


@router.post("/angebot-anfordern", status_code=status.HTTP_201_CREATED, response_model=schemas.PVAnforderungResponse)
async def pv_installationsangebot_anfordern(db: AsyncSession = Depends(database.get_db_async),
                                            current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_haushalt_role(current_user, "POST", "/angebot-anfordern")
    try:
        stmt = (select(models.Nutzer.user_id, func.count(models.PVAnlage.anlage_id).label("anfragen_count"))
                .join(models.PVAnlage, models.Nutzer.user_id == models.PVAnlage.solarteur_id, isouter=True)
                .group_by(models.Nutzer.user_id)
                .order_by("anfragen_count")
                .where(models.Nutzer.rolle == models.Rolle.Solarteure))
        result = await db.execute(stmt)
        solarteur = result.first()

        if not solarteur:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/angebot-anfordern",
                method="POST",
                message="Kein Solarteur verfügbar",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Kein Solarteur verfügbar")

        pv_anlage = models.PVAnlage(
            haushalt_id=current_user.user_id,
            solarteur_id=solarteur.user_id,
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
            solarteur_id=solarteur.user_id
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


# haushalt sieht alle tarife und kann sich für einen entscheiden
@router.post("/tarifantrag/{tarif_id}", response_model=schemas.VertragResponse)
async def tarifantrag(tarif_id: int,
                      current_user: models.Nutzer = Depends(oauth.get_current_user),
                      db: AsyncSession = Depends(database.get_db_async)):

    # Prüfen, ob der angeforderte Tarif existiert
    await check_haushalt_role(current_user, "POST", f"/tarifantrag/{tarif_id}")
    user_id = current_user.user_id
    try:
        query = select(models.Tarif).where((models.Tarif.tarif_id == tarif_id) &
                                           (models.Tarif.active == True))
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
                message=f"Felher beim Abrufen des Tarifs: {e}",
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
            vertragstatus=True,
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
                            detail=f"Tarif {tarif_id} für user {user_id }existiert für user bereits")


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
async def kontakt_aufnehmen_energieberatenden(db: AsyncSession = Depends(database.get_db_async),
                                              current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_haushalt_role(current_user, "POST", "/kontaktaufnahme-energieberatenden")

    try:
        stmt = (
            select(models.Nutzer.user_id)
            .join(models.Energieausweise, models.Nutzer.user_id == models.Energieausweise.energieberater_id,
                  isouter=True)
            .where(models.Nutzer.rolle == models.Rolle.Energieberatende)
            .group_by(models.Nutzer.user_id)
            .order_by(func.count(models.Energieausweise.energieausweis_id))
            .limit(1))
        result = await db.execute(stmt)
        energieberater = result.scalars().first()

        if not energieberater:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/kontaktaufnahme-energieberatenden",
                method="POST",
                message="Kein Energieberatende verfügbar",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Kein Energieberatende verfügbar")

        neue_anfrage = models.Energieausweise(
            haushalt_id=current_user.user_id,
            energieberater_id=energieberater,
            ausweis_status=models.AusweisStatus.AnfrageGestellt
        )

        db.add(neue_anfrage)
        await db.commit()
        await db.refresh(neue_anfrage)

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
            energieberater_id=neue_anfrage.energieberater_id,
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
    await check_haushalt_role(current_user, "GET", f"/all-tarife/{tarif_id}")
    try:
        stmt = select(models.Tarif, models.Nutzer)\
            .join(models.Nutzer, models.Tarif.netzbetreiber_id == models.Nutzer.user_id)\
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


@router.get("/vertraege", response_model=List[schemas.VertragTarifResponse])
async def get_vertraege(db: AsyncSession = Depends(database.get_db_async),
                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_haushalt_role(current_user, "GET", "/vertraege")
    try:
        stmt = select(models.Vertrag, models.Tarif).join(models.Tarif, models.Vertrag.tarif_id == models.Tarif.tarif_id)\
            .where(models.Vertrag.user_id == current_user.user_id)
        result = await db.execute(stmt)
        vertraege = result.all()
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
    

@router.get("/vertraege/{vertrag_id}", response_model=schemas.VertragTarifNBResponse)
async def get_vertrag(vertrag_id: int,
                      db: AsyncSession = Depends(database.get_db_async),
                      current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_haushalt_role(current_user, "GET", f"/vertraege/{vertrag_id}")
    try:
        stmt = select(models.Vertrag, models.Tarif, models.Nutzer)\
            .join(models.Tarif, models.Vertrag.tarif_id == models.Tarif.tarif_id)\
            .join(models.Nutzer, models.Vertrag.netzbetreiber_id == models.Nutzer.user_id)\
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
    endpoint = f"/vertrag-deaktivieren/{vertrag_id}"
    await check_haushalt_role(current_user, "GET", endpoint)
    try:
        stmt = select(models.Vertrag).where(models.Vertrag.vertrag_id == vertrag_id)
        result = await db.execute(stmt)
        vertrag = result.first()[0]
        if not vertrag.vertragstatus:
            logging_error = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=endpoint,
                method="PUT",
                message=f"Vertrag {vertrag_id} is bereits deaktiviert",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Vertrag {vertrag_id} is bereits deaktiviert")
        vertrag.vertragstatus = False
        await db.commit()
        await db.refresh(vertrag)
        return {"message": f"Vertrag {vertrag_id} wurde erfolgreich deaktiviert"}
    except Exception as e:
        raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")