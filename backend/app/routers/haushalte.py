from datetime import MAXYEAR, date
from datetime import date, datetime
from uuid import uuid4
from typing import List

import sqlalchemy
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Path
from sqlalchemy import select, func, exc, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas, database, oauth, types
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.schemas import LoggingSchema, TarifAntragCreate, VertragResponse

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
@router.post("/tarifantrag", response_model=schemas.VertragResponse)
async def tarifantrag(tarifantrag: schemas.TarifAntragCreate, db: AsyncSession = Depends(database.get_db_async)):
    logger.info(f"Tarifantrag erhalten: {tarifantrag}")

    # Prüfen, ob der angeforderte Tarif existiert
    try:
        tarif = await db.get(models.Tarif, tarifantrag.tarif_id)
        if not tarif:
            logger.error(f"Tarif mit ID {tarifantrag.tarif_id} nicht gefunden für Nutzer ID {tarifantrag.user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarif nicht gefunden")
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Tarifs: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen des Tarifs")

    try:
        vertrag = models.Vertrag(
            user_id=tarifantrag.user_id,
            tarif_id=tarifantrag.tarif_id,
            beginn_datum=tarifantrag.beginn_datum,
            end_datum=tarifantrag.end_datum,
            jahresabschlag=tarifantrag.jahresabschlag,
            vertragstatus=tarifantrag.vertragstatus,
            netzbetreiber_id=tarif.netzbetreiber_id
        )
        db.add(vertrag)
        await db.commit()
        await db.refresh(vertrag)
        logger.info(f"Vertrag {vertrag.vertrag_id} erfolgreich erstellt für Nutzer ID {tarifantrag.user_id}")
        return schemas.VertragResponse(
            vertrag_id=vertrag.vertrag_id,
            user_id=vertrag.user_id,
            tarif_id=vertrag.tarif_id,
            beginn_datum=vertrag.beginn_datum,
            end_datum=vertrag.end_datum,
            jahresabschlag=vertrag.jahresabschlag,
            vertragstatus=vertrag.vertragstatus
        )
    except Exception as e:
        logger.error(f"Fehler bei der Erstellung des Vertrags für Nutzer ID {tarifantrag.user_id}: {e}")
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


@router.post("/datenfreigabe", status_code=status.HTTP_200_OK,
             response_model=schemas.HaushaltsDatenFreigabeResponse)
async def daten_freigabe(freigabe_daten: schemas.HaushaltsDatenFreigabe,
                         current_user: models.Nutzer = Depends(oauth.get_current_user),
                         db: AsyncSession = Depends(database.get_db_async)):
    await check_haushalt_role(current_user, "POST", "/datenfreigabe")

    haushaltsdaten = await db.execute(select(models.Haushalte).where(models.Haushalte.user_id == current_user.user_id))
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

    try:
        update_query = (
            update(models.Haushalte)
            .where(models.Haushalte.user_id == current_user.user_id)
            .values(**freigabe_daten.dict(), anfragestatus=True)
        )
        await db.execute(update_query)
        await db.commit()
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
