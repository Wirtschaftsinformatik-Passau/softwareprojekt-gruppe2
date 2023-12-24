from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, exc, update, text
from datetime import datetime
from app import models, schemas, database, oauth, types
import json
from pathlib import Path
from collections import defaultdict, Counter, OrderedDict
from typing import Dict, Union, List, Any
from pydantic import ValidationError
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.config import Settings
from app.schemas import LoggingSchema, TarifCreate, TarifResponse
from app import config
import pandas as pd
import io

router = APIRouter(prefix="/netzbetreiber", tags=["Netzbetreiber"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_netzbetreiber_role(current_user: models.Nutzer, method: str, endpoint: str):
    if current_user.rolle != models.Rolle.Netzbetreiber:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Netzbetreiber",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Netzbetreiber haben Zugriff auf diese Daten")


def is_haushalt(user: models.Nutzer) -> bool:
    return user.rolle == models.Rolle.Haushalte


def validate_pv_anlage(pv_anlage: models.PVAnlage) -> bool:
    # Annahmen für die Netzverträglichkeitsprüfung
    max_kapazitaet_kw = 100.0  # Maximale Kapazität in Kilowatt
    max_installationsflaeche_m2 = 1000.0  # Maximale Installationsfläche in Quadratmetern

    is_within_kapazitaetsgrenze = pv_anlage.kapazitaet <= max_kapazitaet_kw
    is_within_flaechengrenze = pv_anlage.installationsflaeche <= max_installationsflaeche_m2
    is_valid_modulanordnung = pv_anlage.modulanordnung in [models.Orientierung.Sued, models.Orientierung.Suedost,
                                                           models.Orientierung.Suedwest]
    is_valid_montagesystem = pv_anlage.montagesystem != models.Montagesystem.Freilandmontage
    is_valid_schattenanalyse = pv_anlage.schattenanalyse in [models.Schatten.Kein_Schatten,
                                                             models.Schatten.Minimalschatten]

    print(
        f"Prozess Status der PV-Anlage (ID: {is_within_kapazitaetsgrenze}): {is_within_flaechengrenze}, {is_valid_modulanordnung}")
    return all([
        is_within_kapazitaetsgrenze,
        is_within_flaechengrenze,
        is_valid_modulanordnung,
        is_valid_montagesystem,
        is_valid_schattenanalyse
    ])


# Tarif erstellen
@router.post("/tarife", response_model=schemas.TarifResponse, status_code=status.HTTP_201_CREATED)
async def create_tarif(tarif: schemas.TarifCreate, db: AsyncSession = Depends(database.get_db_async),
                       current_user: models.Nutzer = Depends(oauth.get_current_user), ):
    try:
        user_id = current_user.user_id
        tarif.netzbetreiber_id = user_id
        new_tarif = models.Tarif(**tarif.dict())
        db.add(new_tarif)
        await db.commit()
        await db.refresh(new_tarif)
        return new_tarif
    except exc.IntegrityError as e:
        logger.error(f"Tarif konnte nicht erstellt werden: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tarif konnte nicht erstellt werden: {e}")


# Tarif aktualisieren
@router.put("/tarife/{tarif_id}", response_model=schemas.TarifResponse)
async def update_tarif(tarif_id: int, tarif: schemas.TarifCreate,
                       current_user: models.Nutzer = Depends(oauth.get_current_user),
                       db: AsyncSession = Depends(database.get_db_async)):
    try:
        query = select(models.Tarif).where(models.Tarif.tarif_id == tarif_id)

        await check_netzbetreiber_role(current_user, "PUT", "/tarife")
        user_id = current_user.user_id
        query = select(models.Tarif).where((models.Tarif.tarif_id == tarif_id) &
                                           (models.Tarif.user_id == user_id))

        result = await db.execute(query)
        existing_tarif = result.scalar_one_or_none()

        if existing_tarif is None:
            raise HTTPException(status_code=404, detail=f"Tarif mit ID {tarif_id} nicht gefunden")

        for key, value in tarif.dict().items():
            setattr(existing_tarif, key, value)

        await db.commit()
        await db.refresh(existing_tarif)
        return existing_tarif
    except exc.IntegrityError as e:
        logger.error(f"Tarif konnte nicht aktualisiert werden: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tarif konnte nicht aktualisiert werden: {e}")


# Tarif löschen
@router.delete("/tarife/{tarif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tarif(tarif_id: int, db: AsyncSession = Depends(database.get_db_async),
                       current_user: models.Nutzer = Depends(oauth.get_current_user)):
    delete_stmt = select(models.Tarif).where(models.Tarif.tarif_id == tarif_id)

    await check_netzbetreiber_role(current_user, "DELETE", "/tarife/{tarif_id}")

    user_id = current_user.user_id

    # Überprüfen, ob der Tarif existiert
    delete_stmt = select(models.Tarif).where((models.Tarif.tarif_id == tarif_id) &
                                             (models.Tarif.user_id == user_id))
    result = await db.execute(delete_stmt)
    db_tarif = result.scalar_one_or_none()
    if db_tarif is None:
        raise HTTPException(status_code=404, detail="Tarif nicht gefunden")

    await db.delete(db_tarif)
    await db.commit()


# Alle Tarife abrufen
@router.get("/tarife", response_model=List[schemas.TarifResponse])
async def get_tarife(db: AsyncSession = Depends(database.get_db_async)):
    result = await db.execute(select(models.Tarif))
    tarife = result.scalars().all()
    if not tarife:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keine Tarife gefunden")
    return tarife


# Einzelnen Tarif abrufen
@router.get("/tarife/{tarif_id}", response_model=schemas.TarifResponse)
async def get_tarif_by_id(tarif_id: int, db: AsyncSession = Depends(database.get_db_async)):
    query = select(models.Tarif).where(models.Tarif.tarif_id == tarif_id)
    result = await db.execute(query)
    tarif = result.scalar_one_or_none()
    if tarif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarif mit ID {tarif_id} nicht gefunden")
    return tarif


@router.get("/laufzeit", response_model=List[schemas.TarifLaufzeitResponse])
async def count_laufzeit(current_user: models.Nutzer = Depends(oauth.get_current_user),
                         db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user or models.Rolle.Admin, "GET", "/tarife")

    try:
        user_id = current_user.user_id
        select_stmt = select(models.Tarif).where(models.Tarif.user_id == user_id)
        result = await db.execute(select_stmt)
        laufzeiten = result.scalars().all()
        if len(laufzeiten) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Keine Tarife gefunden")
        laufzeiten = [x.laufzeit for x in laufzeiten]
        laufzeit_dict = dict(Counter(laufzeiten))
        laufzeit_response = [{"laufzeit": key, "value": value} for key, value in laufzeit_dict.items()]
        laufzeit_response = sorted(laufzeit_response, key=lambda x: x['laufzeit'])
        return laufzeit_response
    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der Tarife: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der Tarife: {e}")


@router.get("/preisstrukturen", response_model=List[schemas.PreisstrukturenResponse])
async def get_preisstrukturen(current_user: models.Nutzer = Depends(oauth.get_current_user),
                              db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user, "GET", "/preisstrukturen")
    try:
        user_id = current_user.user_id
        select_stmt = select(models.Preisstrukturen).where(models.Preisstrukturen.user_id == user_id)
        result = await db.execute(select_stmt)
        preisstrukturen = result.scalars().all()
        return preisstrukturen
    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der Preisstrktur: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der Preisstrktur: {e}")


@router.get("/preisstrukturen/{preis_id}", response_model=schemas.PreisstrukturenResponse)
async def get_preisstrukturen(preis_id: int, current_user: models.Nutzer = Depends(oauth.get_current_user),
                              db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user, "GET", "/preisstrukturen/{preis_id}")
    try:
        user_id = current_user.user_id
        select_stmt = select(models.Preisstrukturen).where((models.Preisstrukturen.preis_id == preis_id) &
                                                           (models.Preisstrukturen.user_id == user_id))
        result = await db.execute(select_stmt)
        preisstruktur = result.scalars().all()
        if len(preisstruktur) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Preisstruktur mit ID {preis_id} nicht gefunden")
        return preisstruktur[0]
    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der Preisstrktur: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der Preisstrktur: {e}")


@router.post("/preisstrukturen", status_code=status.HTTP_201_CREATED,
             response_model=schemas.PreisstrukturenResponse)
async def create_preisstruktur(preisstruktur: schemas.PreisstrukturenCreate,
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user, "POST", "/preisstrukturen")
    try:
        user_id = current_user.user_id
        preisstruktur.user_id = user_id
        preisstruktur = models.Preisstrukturen(**preisstruktur.dict())
        db.add(preisstruktur)
        await db.commit()
        await db.refresh(preisstruktur)
        logging_info = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="POST",
            message=f"Preisstruktur {preisstruktur.preis_id} erstellt",
            success=True
        )
        logger.info(logging_info.dict())
        return preisstruktur
    except SQLAlchemyError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="POST",
            message=f"SQLAlchemy Fehler beim Erstellen der Preisstruktur: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Erstellen der Preisstruktur")
    except ValidationError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="POST",
            message=f"Validierungsfehler: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=400, detail="Ungültige Eingabedaten")


@router.put("/preisstrukturen/{preis_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.PreisstrukturenResponse)
async def update_preisstruktur(preis_id: int, preisstruktur_data: schemas.PreisstrukturenCreate,
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    await check_netzbetreiber_role(current_user, "PUT", "/preisstrukturen")
    user_id = current_user.user_id
    query = select(models.Preisstrukturen).where((models.Preisstrukturen.preis_id == preis_id) &
                                                 (models.Preisstrukturen.user_id == user_id))
    result = await db.execute(query)
    preisstruktur = result.scalars().first()

    if preisstruktur is None:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/preisstrukturen",
            method="PUT",
            message=f"Preisstruktur mit ID {preis_id} nicht gefunden",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=404, detail=f"Preisstruktur mit ID {preis_id} nicht gefunden")

    try:
        for key, value in preisstruktur_data.dict().items():
            setattr(preisstruktur, key, value)

        await db.commit()
        await db.refresh(preisstruktur)
        logging_info = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/preisstrukturen/{preis_id}",
            method="PUT",
            message=f"Preisstruktur {preis_id} aktualisiert",
            success=True
        )
        logger.info(logging_info.dict())
        return preisstruktur

    except SQLAlchemyError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/preisstrukturen/{preis_id}",
            method="PUT",
            message=f"Fehler beim Aktualisieren der Preisstruktur {preis_id}: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=500, detail="Interner Serverfehler")


@router.post("/dashboard/{haushalt_id}", status_code=status.HTTP_201_CREATED,
             response_model=schemas.DashboardSmartMeterDataResponse)
async def add_dashboard_smartmeter_data(haushalt_id: int,
                                        db: AsyncSession = Depends(database.get_db_async),
                                        file: UploadFile = File(...),
                                        current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "POST", "/dashboard")
    try:
        haushalt_user = await db.get(models.Nutzer, haushalt_id)
        user_id = current_user.user_id
        if not haushalt_user or haushalt_user.rolle != models.Rolle.Haushalte:
            logging_error = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/dashboard",
                method="POST",
                message=f"Nutzer {haushalt_id} ist nicht in der Rolle 'Haushalte'",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=400, detail="Nutzer ist nicht in der Rolle 'Haushalte'")

        df = pd.read_csv(io.StringIO(file.file.read().decode('utf-8')))
        df['Zeit'] = pd.to_datetime(df['Zeit'])

        for _, row in df.iterrows():
            dashboard_data = models.DashboardSmartMeterData(
                haushalt_id=haushalt_id,
                datum=row['Zeit'],
                pv_erzeugung=row['PV(W)'],
                soc=row['SOC(%)'],
                batterie_leistung=row['Batterie(W)'],
                zaehler=row['Zähler(W)'],
                last=row['Last(W)'],
                user_id=user_id
            )
            db.add(dashboard_data)
        await db.commit()

        logging_info = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/dashboard",
            method="POST",
            message=f"Smart-Meter-Daten für Nutzer {haushalt_id} erfolgreich hinzugefügt",
            success=True
        )
        logger.info(logging_info.dict())

        return {"message": "Smart-Meter-Daten erfolgreich hochgeladen"}

    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/dashboard",
            method="POST",
            message=f"Fehler beim Hinzufügen von Smart-Meter-Daten: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")


@router.get("/haushalte", status_code=status.HTTP_200_OK, )
async def get_haushalte(current_user: models.Nutzer = Depends(oauth.get_current_user),
                        db: AsyncSession = Depends(database.get_db_async)):
    try:
        await check_netzbetreiber_role(current_user, "GET", "/haushalte")
        user_id = current_user.user_id
        stmt = select(models.Nutzer, models.Adresse).join(models.Adresse,
                                                          models.Nutzer.adresse_id == models.Adresse.adresse_id).where(
            models.Nutzer.rolle == models.Rolle.Haushalte)
        result = await db.execute(stmt)
        haushalte = result.all()
        response = [{
            "nachname": user.nachname,
            "email": user.email,
            "user_id": user.user_id,
            "vorname": user.vorname,
            "rolle": user.rolle if user.rolle is not None else "unknown",
            "adresse_id": user.adresse_id,
            "geburtsdatum": user.geburtsdatum,
            "telefonnummer": user.telefonnummer,
            "strasse": adresse.strasse,
            "stadt": adresse.stadt,
            "hausnr": adresse.hausnummer,
            "plz": adresse.plz,
        } for user, adresse in haushalte]
        return response
    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/haushalte",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der Haushalte: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der Haushalte: {e}")

    except Exception as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/haushalte",
            method="GET",
            message=f"Fehler beim Abrufen der Haushalte: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Haushalte: {e}")


@router.get("/dashboard/{haushalt_id}", status_code=status.HTTP_200_OK,
            response_model=Union[List[schemas.AggregatedDashboardSmartMeterData],
            List[schemas.AggregatedDashboardSmartMeterDataResponsePV],
            List[schemas.AggregatedDashboardSmartMeterDataResponseSOC],
            List[schemas.AggregatedDashboardSmartMeterDataResponseBatterie],
            List[schemas.AggregatedDashboardSmartMeterDataResponseLast]])
async def get_aggregated_dashboard_smartmeter_data(haushalt_id: int, field: str = "all", period: str = "DAY",
                                                   start: str = "2023-01-01", end: str = "2023-01-30",
                                                   db: AsyncSession = Depends(database.get_db_async),
                                                   current_user: models.Nutzer = Depends(oauth.get_current_user)):
    # TODO: parameter validierung für sql injections
    await check_netzbetreiber_role(current_user, "POST", "/dashboard/{haushalt_id}")
    stmt = select(models.Nutzer.rolle).where(models.Nutzer.user_id == haushalt_id)
    user_id = current_user.user_id
    result = await db.execute(stmt)
    nutzer_rolle = result.scalar_one_or_none()
    if nutzer_rolle is None or nutzer_rolle != models.Rolle.Haushalte:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="dashboard/{haushalt_id}",
            method="POST",
            message="Haushalt nicht gefunden oder Rolle unpassend",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=404, detail="Nutzer ist nicht in der Rolle 'Haushalte'")
    try:
        table_name = "dashboard_smartmeter_data" if config.settings.OS == 'Linux' else '"Dashboard_smartmeter_data"'
        if field == "all":
            raw_sql = text(
                f"""
                SELECT 
                DATE_TRUNC('{period}', datum), 
                sum(pv_erzeugung) as gesamt_pv_erzeugung,
                avg(soc) as gesamt_soc,
                sum(batterie_leistung) as gesamt_batterie_leistung,
                sum(last) as gesamt_last
                from {table_name}
                WHERE user_id = {user_id} and haushalt_id = {haushalt_id} 
                and datum >= '{start}' and  datum < '{end}'
                group by 
                DATE_TRUNC('{period}', datum) 
                ORDER BY DATE_TRUNC('{period}', datum) 
                """
            )
        elif field == "pv":
            raw_sql = text(
                f"""
                SELECT 
                DATE_TRUNC('{period}', datum), 
                sum(pv_erzeugung) as gesamt_pv_erzeugung
                from {table_name} 
                WHERE user_id = {user_id} and haushalt_id = {haushalt_id} 
                and datum >= '{start}' and  datum < '{end}'
                group by 
                DATE_TRUNC('{period}', datum) 
                ORDER BY DATE_TRUNC('{period}', datum) 
                            """
            )

        elif field == "soc":
            raw_sql = text(
                f"""
                SELECT 
                DATE_TRUNC('{period}', datum), 
                avg(soc) as gesamt_soc
                from {table_name}
                WHERE user_id = {user_id} and haushalt_id = {haushalt_id}  
                and datum >= '{start}' and  datum < '{end}'
                group by 
                DATE_TRUNC('{period}', datum) 
                ORDER BY DATE_TRUNC('{period}', datum) 
                            """
            )

        elif field == "batterie":
            raw_sql = text(
                f"""
                SELECT 
                DATE_TRUNC('{period}', datum),
                sum(batterie_leistung) as gesamt_batterie_leistung
                from {table_name}
                WHERE user_id = {user_id} and haushalt_id = {haushalt_id} 
                and datum >= '{start}' and  datum < '{end}'
                group by 
                DATE_TRUNC('{period}', datum) 
                ORDER BY DATE_TRUNC('{period}', datum) 
                """
            )

        elif field == "last":
            raw_sql = text(
                f"""
                SELECT 
                DATE_TRUNC('{period}', datum), 
                sum(last) as gesamt_last
                from {table_name}
                WHERE user_id = {user_id} and haushalt_id = {haushalt_id} 
                and datum >= '{start}' and  datum < '{end}'
                group by 
                DATE_TRUNC('{period}', datum) 
                ORDER BY DATE_TRUNC('{period}', datum) 
                """
            )

        else:
            raise HTTPException(status_code=400, detail="Ungültiges Feld")

        result = await db.execute(raw_sql)
        aggregated_data = result.fetchall()

        if not aggregated_data:
            raise HTTPException(status_code=404, detail="Keine Dashboard-Daten für diesen Haushalt gefunden")

        logging_info = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="dashboard/{haushalt_id}",
            method="GET",
            message="Dashboard-Daten erfolgreich abgerufen",
            success=True
        )
        logger.info(logging_info.dict())

        if field == "all":
            return [schemas.AggregatedDashboardSmartMeterData(
                datum=row[0].isoformat() if row[0] else None,
                gesamt_pv_erzeugung=row[1],
                gesamt_soc=row[2],
                gesamt_batterie_leistung=row[3],
                gesamt_last=row[4]
            ) for row in aggregated_data]

        elif field == "pv":
            return [schemas.AggregatedDashboardSmartMeterDataResponsePV(
                x=row[0].isoformat() if row[0] else None,
                y=row[1]
            ) for row in aggregated_data[:1000]]

        elif field == "soc":
            return [schemas.AggregatedDashboardSmartMeterDataResponseSOC(
                x=row[0].isoformat() if row[0] else None,
                y=row[1]
            ) for row in aggregated_data]

        elif field == "batterie":
            return [schemas.AggregatedDashboardSmartMeterDataResponseBatterie(
                x=row[0].isoformat() if row[0] else None,
                y=row[1]
            ) for row in aggregated_data]

        elif field == "last":
            return [schemas.AggregatedDashboardSmartMeterDataResponseLast(
                x=row[0].isoformat(),
                y=row[1]
            ) for row in aggregated_data]

    except HTTPException as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/dashboard",
            method="GET",
            message=f"Ausnahme aufgetreten: {e.detail}",
            success=False
        )
        logger.error(logging_error.dict())
        raise


@router.put("/nvpruefung/{anlage_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.NetzvertraeglichkeitspruefungResponse)
async def durchfuehren_netzvertraeglichkeitspruefung(anlage_id: int, db: AsyncSession = Depends(database.get_db_async),
                                                     current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "PUT", f"/netzbetreiber/nvpruefung/{anlage_id}")

    stmt = select(models.PVAnlage).where(models.PVAnlage.anlage_id == anlage_id)
    result = await db.execute(stmt)
    pv_anlage = result.scalar_one_or_none()

    if pv_anlage is None:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/netzbetreiber/nvpruefung/{anlage_id}",
            method="PUT",
            message="PV-Anlage nicht gefunden",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PV-Anlage nicht gefunden")

    if pv_anlage.prozess_status != models.ProzessStatus.PlanErstellt:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/netzbetreiber/nvpruefung/{anlage_id}",
            method="PUT",
            message="PV-Anlage ist nicht im Status 'PlanErstellt'",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="PV-Anlage ist nicht im Status 'PlanErstellt'")

    is_compatible = validate_pv_anlage(pv_anlage)

    update_stmt = (
        update(models.PVAnlage)
        .where(models.PVAnlage.anlage_id == anlage_id)
        .values(nvpruefung_status=is_compatible)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(update_stmt)
    await db.commit()

    logging_obj = LoggingSchema(
        user_id=current_user.user_id,
        endpoint=f"/netzbetreiber/nvpruefung/{anlage_id}",
        method="PUT",
        message="Netzverträglichkeitsprüfung durchgeführt",
        success=True
    )
    logger.info(logging_obj.dict())

    return {"anlage_id": anlage_id, "nvpruefung_status": is_compatible}


@router.get("/anlagen", status_code=status.HTTP_200_OK)
async def anlage_ueberpruefung(db: AsyncSession = Depends(database.get_db_async),
                               current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", "/anlagen")

    stmt = select(models.PVAnlage).where(models.PVAnlage.netzbetreiber_id == None)
    result = await db.execute(stmt)
    pv_anlage = result.scalars().all()


@router.put("/einspeisezusage/{anlage_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.EinspeisezusageResponse)
async def einspeisezusage_erteilen(anlage_id: int, db: AsyncSession = Depends(database.get_db_async),
                                   current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "PUT", f"/netzbetreiber/einspeisezusage/{anlage_id}")

    stmt = select(models.PVAnlage).where(models.PVAnlage.anlage_id == anlage_id)
    result = await db.execute(stmt)
    pv_anlage = result.scalars().first()

    if pv_anlage is None:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/netzbetreiber/einspeisezusage/{anlage_id}",
            method="PUT",
            message="PV-Anlage nicht gefunden",
            success=True
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PV-Anlage nicht gefunden")

    if not pv_anlage.nvpruefung_status:
        logging_obj = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/netzbetreiber/einspeisezusage/{anlage_id}",
            method="PUT",
            message="Netzverträglichkeitsprüfung nicht bestanden",
            success=True
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Netzverträglichkeitsprüfung nicht bestanden")

    pv_anlage.prozess_status = models.ProzessStatus.Genehmigt
    db.add(pv_anlage)
    await db.commit()

    logging_obj = LoggingSchema(
        user_id=current_user.user_id,
        endpoint=f"/netzbetreiber/einspeisezusage/{anlage_id}",
        method="PUT",
        message="Einspeisezusage erteilt",
        success=True
    )
    logger.info(logging_obj.dict())

    return {"message": "Einspeisezusage erfolgreich erteilt", "anlage_id": anlage_id}


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


@router.get("/einspeisezusagen", response_model=List[schemas.AngebotVorschlag])
async def get_einspeisezusagen_vorschlag(db: AsyncSession = Depends(database.get_db_async),
                                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", f"/netzbetreiber/einspeisezusagen")
    try:
        stmt = select(models.PVAnlage).where((models.PVAnlage.netzbetreiber_id is None) or
                                             (models.PVAnlage.prozess_status != models.ProzessStatus.Genehmigt))
        result = await db.execute(stmt)
        pv_anlagen = result.scalars().all()

        response = [{
            "anlage_id": x.anlage_id,
            "haushalt_id": x.haushalt_id,
            "solarteur_id": x.solarteur_id,
            "modultyp": x.modultyp,
            "kapazitaet": x.kapazitaet,
            "installationsflaeche": x.installationsflaeche,
            "installationsdatum": x.installationsdatum,
            "modulanordnung": x.modulanordnung,
            "kabelwegfuehrung": x.kabelwegfuehrung,
            "montagesystem": x.montagesystem,
            "schattenanalyse": x.schattenanalyse,
            "wechselrichterposition": x.wechselrichterposition,
            "installationsplan": x.installationsplan,
            "prozess_status": x.prozess_status,
            "nvpruefung_status": x.nvpruefung_status
        } for x in pv_anlagen]

        return response

    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/einspeisezusagen",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der PV-Anlagen: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der PV-Anlagen: {e}")


@router.get("/einspeisezusagen/{anlage_id}", response_model=List[schemas.AngebotVorschlag])
async def get_einspeisezusagen_vorschlag(db: AsyncSession = Depends(database.get_db_async),
                                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", f"/netzbetreiber/einspeisezusagen")
    try:
        stmt = select(models.PVAnlage).where((models.PVAnlage.netzbetreiber_id is None) or
                                             (models.PVAnlage.prozess_status != models.ProzessStatus.Genehmigt))
        result = await db.execute(stmt)
        pv_anlagen = result.scalars().all()

        response = [{
            "anlage_id": x.anlage_id,
            "haushalt_id": x.haushalt_id,
            "solarteur_id": x.solarteur_id,
            "modultyp": x.modultyp,
            "kapazitaet": x.kapazitaet,
            "installationsflaeche": x.installationsflaeche,
            "installationsdatum": x.installationsdatum,
            "modulanordnung": x.modulanordnung,
            "kabelwegfuehrung": x.kabelwegfuehrung,
            "montagesystem": x.montagesystem,
            "schattenanalyse": x.schattenanalyse,
            "wechselrichterposition": x.wechselrichterposition,
            "installationsplan": x.installationsplan,
            "prozess_status": x.prozess_status,
            "nvpruefung_status": x.nvpruefung_status
        } for x in pv_anlagen]

        return response

    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/einspeisezusagen",
            method="GET",
            message=f"SQLAlchemy Fehler beim Abrufen der PV-Anlagen: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der PV-Anlagen: {e}")
