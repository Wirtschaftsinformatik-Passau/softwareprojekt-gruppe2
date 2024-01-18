from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import exc, update, text
from app import models, schemas, database, oauth
from collections import Counter
from typing import Union, List
from pydantic import ValidationError
import logging
from logging.config import dictConfig

from app.logger import LogConfig
from app.routers.users import register_user
from app.schemas import LoggingSchema, TarifCreate, TarifResponse, TarifCreate, TarifResponse
from app import types
from app import config
import pandas as pd
import io
from datetime import datetime, timedelta, date

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


async def check_netzbetreiber_role_or_haushalt(current_user: models.Nutzer, method: str, endpoint: str):
    if current_user.rolle not in [models.Rolle.Netzbetreiber, models.Rolle.Haushalte]:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Netzbetreiber oder Haushalt",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Netzbetreiber und Haushalte haben Zugriff auf diese Daten")

def is_haushalt(user: models.Nutzer) -> bool:
    return user.rolle == models.Rolle.Haushalte


def validate_pv_anlage(pv_anlage: models.PVAnlage) -> bool:
    # Annahmen für die Netzverträglichkeitsprüfung
    max_kapazitaet_kw = 100.0  # Maximale Kapazität in Kilowatt
    max_installationsflaeche_m2 = 1000.0  # Maximale Installationsfläche in Quadratmetern
    try:
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
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"Fehlende Daten zur Berechnung. Angebot muss erst erstellt werden")


# Tarif erstellen
@router.post("/tarife", response_model=schemas.TarifResponse, status_code=status.HTTP_201_CREATED)
async def create_tarif(tarif: schemas.TarifCreate, db: AsyncSession = Depends(database.get_db_async),
                       current_user: models.Nutzer = Depends(oauth.get_current_user), ):
    try:
        user_id = current_user.user_id
        tarif.netzbetreiber_id = user_id
        new_tarif = models.Tarif(**tarif.dict())
        new_tarif.active = True
        db.add(new_tarif)
        await db.commit()
        await db.refresh(new_tarif)
        return new_tarif
    except exc.IntegrityError as e:
        logger.error(f"Tarif konnte nicht erstellt werden: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tarif konnte nicht erstellt werden: {e}")


# Tarif aktualisieren
@router.put("/tarife/{tarif_id}", response_model=schemas.TarifResponse)
async def update_tarif(tarif_id: int, tarif: schemas.TarifCreate, db: AsyncSession = Depends(database.get_db_async)):
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
async def get_tarife(db: AsyncSession = Depends(database.get_db_async),
                     current_user: models.Nutzer = Depends(oauth.get_current_user)):
    #TODO: nur tarife von netzbetreiber ausgeben
    await check_netzbetreiber_role(current_user, "GET", "/tarife")
    user_id = current_user.user_id
    result = await db.execute(select(models.Tarif).where(models.Tarif.netzbetreiber_id == user_id))
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
        select_stmt = select(models.Tarif).where(models.Tarif.netzbetreiber_id == user_id)
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


# haben wir einen datencheck drin, das nichts falsches hochgeladen wird??
@router.post("/dashboard/{haushalt_id}", status_code=status.HTTP_201_CREATED,
             response_model=schemas.DashboardSmartMeterDataResponse)
async def add_dashboard_smartmeter_data(haushalt_id: int,
                                        db: AsyncSession = Depends(database.get_db_async),
                                        file: UploadFile = File(...),
                                        current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role_or_haushalt(current_user, "POST", "/dashboard")
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
        await check_netzbetreiber_role_or_haushalt(current_user, "GET", "/haushalte")
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
    try:
        await check_netzbetreiber_role_or_haushalt(current_user, "POST", "/dashboard/{haushalt_id}")

        if period not in ["MINUTE", "HOUR", "DAY", "WEEK", "MONTH"]:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"dashboard/{haushalt_id}",
                method="GET",
                message="Ungültiger Zeitraum angegeben",
                success=False
            )
            logger.error(logging_obj.dict())
            raise ValueError("Ungültiger Zeitraum angegeben")

        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"dashboard/{haushalt_id}",
                method="GET",
                message="Ungültiges Datumsformat",
                success=False
            )
            logger.error(logging_obj.dict())
            raise ValueError("Ungültiges Datumsformat. Bitte verwenden Sie YYYY-MM-DD.")

        stmt = select(models.Nutzer.rolle).where(models.Nutzer.user_id == haushalt_id)
        user_id = current_user.user_id
        result = await db.execute(stmt)
        nutzer_rolle = result.scalar_one_or_none()
        if nutzer_rolle is None or nutzer_rolle != models.Rolle.Haushalte:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"dashboard/{haushalt_id}",
                method="GET",
                message="Haushalt nicht gefunden oder Rolle unpassend",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Nutzer ist nicht in der Rolle 'Haushalte'")

        table_name = "dashboard_smartmeter_data" if config.settings.OS == 'Linux' else '"Dashboard_smartmeter_data"'

        # Determine the fields and GROUP BY clause based on the 'field' parameter
        fields, group_by = determine_query_parts(field)

        params = {
            "user_id": user_id,
            "haushalt_id": haushalt_id,
            "start": start_date,
            "end": end_date,
            "period": period
        }

        query_base = f"""
                    SELECT 
                    DATE_TRUNC(:period, datum) as period, 
                    {', '.join(fields)}
                    from {table_name}
                    WHERE user_id = :user_id and haushalt_id = :haushalt_id  
                    and datum >= :start and datum < :end
                    {group_by}
                    ORDER BY DATE_TRUNC(:period, datum) 
                """

        # Generate the final query
        raw_sql = text(query_base.format(fields=','.join(fields), group_by=group_by))

        result = await db.execute(raw_sql, params)
        aggregated_data = result.fetchall()

        if not aggregated_data:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="dashboard/{haushalt_id}",
                method="GET",
                message="Keine Dashboard-Daten für diesen Haushalt gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Keine Dashboard-Daten für diesen Haushalt gefunden")

        logging_info = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="dashboard/{haushalt_id}",
            method="GET",
            message="Dashboard-Daten erfolgreich abgerufen",
            success=True
        )
        logger.info(logging_info.dict())

        return process_aggregated_data(field, aggregated_data)

    except ValueError as ve:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/dashboard",
            method="GET",
            message=f"Fehler bei der Eingabeüberprüfung: {ve}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=400, detail=str(ve))

    except HTTPException as he:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/dashboard",
            method="GET",
            message=f"HTTP Fehler: {he.detail}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise

    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/dashboard",
            method="GET",
            message=f"Unerwarteter Fehler: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail="Ein unerwarteter Fehler ist aufgetreten")


def determine_query_parts(field):
    # Initialize variables for fields to select and the GROUP BY clause
    fields = []
    group_by = "GROUP BY DATE_TRUNC(:period, datum)"

    # Define the fields and GROUP BY clause based on the 'field' parameter
    if field == "all":
        fields = [
            "sum(pv_erzeugung) as gesamt_pv_erzeugung",
            "avg(soc) as gesamt_soc",
            "sum(batterie_leistung) as gesamt_batterie_leistung",
            "sum(last) as gesamt_last"
        ]
    elif field == "pv":
        fields = ["sum(pv_erzeugung) as gesamt_pv_erzeugung"]
    elif field == "soc":
        fields = ["avg(soc) as gesamt_soc"]
    elif field == "batterie":
        fields = ["sum(batterie_leistung) as gesamt_batterie_leistung"]
    elif field == "last":
        fields = ["sum(last) as gesamt_last"]
    else:
        # If an invalid field is provided, raise an error
        raise ValueError("Ungültiges Feld: {}".format(field))

    # Return the fields and the GROUP BY clause
    return fields, group_by


def process_aggregated_data(field, aggregated_data):
    # Process and return the data based on the 'field' parameter
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
        ) for row in aggregated_data]

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
            x=row[0].isoformat() if row[0] else None,
            y=row[1]
        ) for row in aggregated_data]

    else:
        # Handle unexpected field values
        raise ValueError("Unbekanntes Feld: {}".format(field))


# vor einspeisezusagen
@router.put("/nvpruefung/{anlage_id}", status_code=status.HTTP_202_ACCEPTED,
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
        # wenn nv pruedung false kommt 412 zurück
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail="Netzverträglichkeitsprüfung nicht bestanden")

    pv_anlage.prozess_status = models.ProzessStatus.Genehmigt
    pv_anlage.netzbetreiber_id = current_user.user_id
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
        # Hier holen wir den aktiven Vertrag des Nutzers, um den Jahresabschlag zu erhalten.
        vertrag_query = select(models.Vertrag).where(
            (models.Vertrag.user_id == rechnung.user_id) & 
            (models.Vertrag.vertragstatus == models.Vertragsstatus.Laufend)
        )
        vertrag_result = await db.execute(vertrag_query)
        aktiver_vertrag = vertrag_result.scalar_one_or_none()

        if aktiver_vertrag is None:
            raise HTTPException(status_code=404, detail="Aktiver Vertrag nicht gefunden")

        # Setzen des Jahresabschlags als Rechnungsbetrag
        rechnung_dict = rechnung.dict()
        rechnung_dict["rechnungsbetrag"] = aktiver_vertrag.jahresabschlag

        neue_rechnung = models.Rechnungen(**rechnung_dict)
        db.add(neue_rechnung)
        await db.commit()
        await db.refresh(neue_rechnung)
        return neue_rechnung
    except SQLAlchemyError as e:
        logger.error(f"Rechnung konnte nicht erstellt werden: {e}")
        raise HTTPException(status_code=500, detail=f"Rechnung konnte nicht erstellt werden: {e}")


@router.get("/pv-angenommen", response_model=List[schemas.NetzbetreiberEinspeisungDetail])
async def get_angenommene_pv_anlagen(db: AsyncSession = Depends(database.get_db),
                                     current_user: models.Nutzer = Depends(oauth.get_current_user)):
    try:
        if current_user.rolle != models.Rolle.Netzbetreiber:
            raise HTTPException(status_code=403, detail="Nicht autorisiert")

        stmt = select(models.PVAnlage).where(models.PVAnlage.netzbetreiber_id == current_user.user_id)
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
        logger.error(f"SQLAlchemy Fehler beim Abrufen der PV-Anlagen: {e}")
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der PV-Anlagen: {e}")


@router.get("/einspeisezusagen", response_model=List[schemas.PVSolarteuerResponse])
async def get_einspeisezusagen_vorschlag(prozess_status: List[types.ProzessStatus] =  Query(types.ProzessStatus.PlanErstellt, alias="prozess_status"),
                                         db: AsyncSession = Depends(database.get_db_async),
                                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", f"/netzbetreiber/einspeisezusagen")
    try:
        if prozess_status[0] == types.ProzessStatus.PlanErstellt and (
                len(prozess_status) == 2 or len(prozess_status) == 1):
            query = (select(models.PVAnlage, models.Nutzer, models.Adresse)
                     .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                     .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                     .where(models.PVAnlage.prozess_status == models.ProzessStatus.PlanErstellt))

        else:
            query = (select(models.PVAnlage, models.Nutzer, models.Adresse)
                     .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                     .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id))

            if prozess_status:
                query = query.where((models.PVAnlage.prozess_status.in_(prozess_status))
                                    & (models.PVAnlage.netzbetreiber_id == current_user.user_id))

        result = await db.execute(query)
        anfragen = result.all()

        if not anfragen:
            return []

        response = [{
            "anlage_id": angebot.anlage_id,
            "haushalt_id": angebot.haushalt_id,
            "prozess_status": angebot.prozess_status,
            "vorname": nutzer.vorname,
            "nachname": nutzer.nachname,
            "email": nutzer.email,
            "strasse": adresse.strasse,
            "hausnummer": adresse.hausnummer,
            "plz": adresse.plz,
            "stadt": adresse.stadt
        } for angebot, nutzer, adresse in anfragen]
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


@router.get("/einspeisezusagen/{anlage_id}", response_model=schemas.NetzbetreiberEinspeisungDetail)
async def get_einspeisezusagen_vorschlag(anlage_id: int,
                                         db: AsyncSession = Depends(database.get_db_async),
                                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", f"/netzbetreiber/einspeisezusagen")
    try:
        stmt = (select(models.PVAnlage, models.Nutzer, models.Adresse)
                     .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                     .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                .where((models.PVAnlage.anlage_id == anlage_id)))
        result = await db.execute(stmt)
        pv_anlage = result.first()

        response = {
            "anlage_id": pv_anlage[0].anlage_id,
            "haushalt_id": pv_anlage[0].haushalt_id,
            "solarteur_id": pv_anlage[0].solarteur_id,
            "modultyp": pv_anlage[0].modultyp,
            "kapazitaet": pv_anlage[0].kapazitaet,
            "installationsflaeche": pv_anlage[0].installationsflaeche,
            "installationsdatum": pv_anlage[0].installationsdatum,
            "modulanordnung": pv_anlage[0].modulanordnung,
            "kabelwegfuehrung": pv_anlage[0].kabelwegfuehrung,
            "montagesystem": pv_anlage[0].montagesystem,
            "schattenanalyse": pv_anlage[0].schattenanalyse,
            "wechselrichterposition": pv_anlage[0].wechselrichterposition,
            "installationsplan": pv_anlage[0].installationsplan,
            "prozess_status": pv_anlage[0].prozess_status,
            "nvpruefung_status": pv_anlage[0].nvpruefung_status,
            "vorname": pv_anlage[1].vorname,
            "nachname": pv_anlage[1].nachname,
            "strasse": pv_anlage[2].strasse,
            "hausnr": pv_anlage[2].hausnummer,
            "plz": pv_anlage[2].plz,
            "stadt": pv_anlage[2].stadt

        }

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


@router.put("/tarife/deactivate/{tarif_id}", status_code=status.HTTP_200_OK)
async def deactivate_tarif(tarif_id: int, db: AsyncSession = Depends(database.get_db_async),
                           current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "PUT", f"/netzbetreiber/tarif/deactivate/{tarif_id}")
    try:
        stmt = select(models.Tarif).where(models.Tarif.tarif_id == tarif_id)
        result = await db.execute(stmt)
        tarifs = result.scalars().all()
        if len(tarifs) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarif nicht gefunden")
        tarif = tarifs[0]
        tarif.active = False
        db.add(tarif)
        await db.commit()
        return {"message": "Tarif erfolgreich deaktiviert"}
    except exc.IntegrityError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/tarif/deactivate/{id}",
            method="PUT",
            message=f"SQLAlchemy Fehler beim Deaktivieren des Tarifs: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Deaktivieren des Tarifs: {e}")


@router.get("/kuendigungsanfragen", response_model=List[schemas.KündigungsanfrageResponse])
async def get_kuendigungsanfragen(db: AsyncSession = Depends(database.get_db_async),
                                  current_user: models.Nutzer = Depends(oauth.get_current_user)):
    try:
        query = select(models.Vertrag).where((models.Vertrag.netzbetreiber_id == current_user.user_id) &
                                              (models.Vertrag.vertragstatus == models.Vertragsstatus.Gekuendigt_Unbestaetigt))
        result = await db.execute(query)
        kuendigungsanfragen = result.scalars().all()
        return kuendigungsanfragen
    except SQLAlchemyError as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kuendigungsanfragen",
            method="PUT",
            message=f"SQLAlchemy Fehler beim Abrufen der Kuendigungsanfragen: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"SQLAlchemy Fehler beim Abrufen der Kuendigungsanfragen: {e}")


@router.put("/kuendigungsanfragenbearbeitung/{vertrag_id}")
async def kuendigungsanfragenbearbeitung(vertrag_id: int, aktion: str,
                                         db: AsyncSession = Depends(database.get_db_async),
                                         current_user: models.Nutzer = Depends(oauth.get_current_user)):
    try:
        # Abrufen der Kündigungsanfrage
        query = select(models.Vertrag).where((models.Vertrag.netzbetreiber_id == current_user.user_id) &
                                            (models.Vertrag.vertragstatus == models.Vertragsstatus.Gekuendigt_Unbestaetigt) &
                                             (models.Vertrag.vertrag_id == vertrag_id))
        result = await db.execute(query)
        anfrage = result.scalar_one_or_none()

        if anfrage is None:
            raise HTTPException(status_code=404, detail="Kündigungsanfrage nicht gefunden")

        if aktion == "bestaetigen":
            # Kündigung bestätigen und den Vertragstatus aktualisieren
            anfrage.bestätigt = True
            anfrage.vertragstatus = models.Vertragsstatus.Gekuendigt
         
            # Berechne den zeitanteiligen Jahresabschlag
            jahresanfang = date(date.today().year, 1, 1)
            tage_seit_jahresanfang = (date.today() - jahresanfang).days
            zeitanteiliger_jahresabschlag = anfrage.jahresabschlag * (tage_seit_jahresanfang / 365)

            # Erstelle eine Rechnung für den gekündigten Vertrag
            rechnung = models.Rechnungen(
                user_id=anfrage.user_id,
                rechnungsbetrag=zeitanteiliger_jahresabschlag,
                rechnungsdatum=datetime.now(),
                faelligkeitsdatum=datetime.now() + timedelta(days=30),
                rechnungsart=models.Rechnungsart.Netzbetreiber_Rechnung,
                zeitraum=datetime.now()
            )
            db.add(rechnung)
            logging_msg = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/kuendigungsanfragenbearbeitung/{vertrag_id}/{aktion}",
                method="PUT",
                message=f" Kündigung wurde bestätigt von {current_user.user_id}",
                success=True
            )
            logger.info(logging_msg.dict())

        elif aktion == "ablehnen":
            anfrage.vertragstatus = models.Vertragsstatus.Laufend
            logging_msg = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/kuendigungsanfragenbearbeitung/{vertrag_id}/{aktion}",
                method="PUT",
                message=f" Kündigung wurde abgelehnt von {current_user.user_id}",
                success=True
            )
            logger.info(logging_msg.dict())
        else:
            logging_error = LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/kuendigungsanfragenbearbeitung/{vertrag_id}/{aktion}",
                method="PUT",
                message=f" Ungültige aktion {aktion}",
                success=False
            )
            logger.info(logging_error.dict())
            raise HTTPException(status_code=400, detail=f"Ungültige aktion {aktion}")
        await db.commit()
        return anfrage
    except SQLAlchemyError as e:
        await db.rollback()
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kuendigungsanfragenbearbeitung/{vertrag_id}/{aktion}",
            method="PUT",
            message=f"Ungültige aktion {aktion}",
            success=False
        )
        logger.info(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"Fehler bei der Verarbeitung der Kündigungsanfrage {e}")


@router.get("/vertraege", response_model=List[schemas.VertragTarifResponse])
async def get_vertraege(vertragsstatus: str = "all",
                        db: AsyncSession = Depends(database.get_db_async),
                        current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", "/vertraege")
    try:
        stmt = select(models.Vertrag, models.Tarif).join(models.Tarif,
                                                         models.Vertrag.tarif_id == models.Tarif.tarif_id).where(
            models.Vertrag.netzbetreiber_id == current_user.user_id)
        if vertragsstatus != "all":
            try:
                vertragsstatus = models.Vertragsstatus(vertragsstatus)
                stmt = stmt.where(models.Vertrag.vertragstatus == vertragsstatus)
            except ValueError as e:
                logging_error = LoggingSchema(
                    user_id=current_user.user_id,
                    endpoint=f"/vertraege/{vertragsstatus}",
                    method="PUT",
                    message=f"Ungültigher vertragsstatus {e}",
                    success=False
                )
                logger.info(logging_error.dict())
                raise HTTPException(status_code=404, detail=f"Ungültigher vertragsstatus {e}")

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


@router.get("/vertraege/{vertrag_id}", response_model=schemas.VertragTarifNBResponse)
async def get_vertrag(vertrag_id: int,
                      db: AsyncSession = Depends(database.get_db_async),
                      current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_netzbetreiber_role(current_user, "GET", f"/vertraege/{vertrag_id}")
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


@router.post("/mitarbeiter", status_code=status.HTTP_201_CREATED)
async def create_mitarbeiter(nutzer: schemas.NutzerCreate,
                             db: AsyncSession = Depends(database.get_db_async),
                             current_user: models.Nutzer = Depends(oauth.get_current_user)):

    await check_netzbetreiber_role(current_user, "POST", "/mitarbeiter")
    if nutzer.rolle != models.Rolle.Netzbetreiber.value:
        raise HTTPException(status_code=403, detail="Netzbetreiber kann nur Netzbetreiber erstellen")

    netzbetreiber = await db.get(models.Netzbetreiber, current_user.user_id)
    if not netzbetreiber.arbeitgeber:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/mitarbeiter",
            method="POST",
            message=f"Netzbetreiber {netzbetreiber.user_id} ist kein Arbeitgeber",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail=f"Netzbetreiber {netzbetreiber.user_id} ist kein Arbeitgeber")

    user_id = await register_user(nutzer, db)

    try:
        mitarbeiter = models.Arbeitsverhältnis(arbeitgeber_id=current_user.user_id, arbeitnehmer_id=user_id)
        db.add(mitarbeiter)
        await db.commit()
        await db.refresh(mitarbeiter)

        logging_info = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/mitarbeiter",
            method="POST",
            message=f"Mitarbeiter {user_id} erfolgreich erstellt",
            success=True
        )
        logger.info(logging_info.dict())
        return {"arbeitnehmer_id": user_id, "arbeitgeber_id": current_user.user_id}

    except Exception as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/mitarbeiter",
            method="POST",
            message=f"Fehler beim Erstelln der Mitarbeiter {e}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"Fehler beim Erstelln der Mitarbeiter {e}")


@router.get("/mitarbeiter", response_model=List[schemas.UserOut])
async def get_mitarbeiter(db: AsyncSession = Depends(database.get_db_async),
                          current_user: models.Nutzer = Depends(oauth.get_current_user)):
    stmt = (
        select(models.Nutzer, models.Adresse)
        .join(models.Arbeitsverhältnis, models.Nutzer.user_id == models.Arbeitsverhältnis.arbeitnehmer_id)
        .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id, isouter=True)
        .where(models.Arbeitsverhältnis.arbeitgeber_id == current_user.user_id)
    )
    try:
        result = await db.execute(stmt)
        user_adresse_pairs = result.all()
        users_out = [{
            "nachname": user.nachname,
            "email": user.email,
            "user_id": user.user_id,
            "vorname": user.vorname,
            "rolle": user.rolle if user.rolle is not None else "unknown",
            "adresse_id": user.adresse_id,
            "geburtsdatum": str(user.geburtsdatum),
            "telefonnummer": user.telefonnummer,
            "strasse": adresse.strasse,
            "stadt": adresse.stadt,
            "hausnr": adresse.hausnummer,
            "plz": adresse.plz,

        } for user, adresse in user_adresse_pairs]
        return users_out
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Error beim User Abfragen: {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Error beim User Abfragen: {e.orig}"
            msg = "Es gab einen Fehler bei der user Abfrage."
        logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/users/", method="GET",
                                            message=logging_msg, success=False)
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


@router.get("/check-arbeitgeber", status_code=status.HTTP_200_OK)
async def check_arbeitgeber(db: AsyncSession = Depends(database.get_db_async),
                            current_user: models.Nutzer = Depends(oauth.get_current_user)):
    try:
        netzbetreiber = await db.get(models.Netzbetreiber, current_user.user_id)
        if not netzbetreiber.arbeitgeber:
            return {"is_arbeitgeber": False}

        return {"is_arbeitgeber": True}

    except Exception as e:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/check-arbeitgeber",
            method="GET",
            message=f"Fehler beim Überprüfen des Arbeitgebers {e}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=409, detail=f"Fehler beim Überprüfen des Arbeitgebers {e}")
