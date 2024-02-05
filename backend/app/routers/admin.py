import traceback
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exc
from sqlalchemy import exc
from datetime import datetime, date, timedelta
from app import models, schemas, database, oauth
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Union, List, Any
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.config import Settings
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_admin_role(current_user: models.Nutzer, method: str, endpoint: str):
    """
    Überprüft, ob der aktuelle Benutzer die Rolle des Administrators hat.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.
        method (str): Die HTTP-Methode der aktuellen Anfrage.
        endpoint (str): Der Endpunkt, auf den zugegriffen wird.

    Raises:
        HTTPException: Wenn der Benutzer kein Administrator ist.
    """
    if current_user.rolle != models.Rolle.Admin:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Admin",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nur Admins haben Zugriff auf diese Daten")


async def check_log_file_existence(log_file_path: Path, current_user_id: int, endpoint: str) -> None:
    """
    Überprüft, ob die Protokolldatei unter dem angegebenen Pfad existiert.

    Args:
        log_file_path (Path): Der Pfad der Protokolldatei.
        current_user_id (int): Die ID des aktuellen Benutzers.
        endpoint (str): Der Endpunkt, auf den zugegriffen wird.

    Raises:
        HTTPException: Wenn die Protokolldatei nicht existiert.
    """
    if not log_file_path.exists():
        logging_error = schemas.LoggingSchema(
            user_id=current_user_id,
            endpoint=endpoint,
            method="GET",
            message="Log-Datei existiert nicht",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=404, detail="Log-Datei nicht gefunden")


def handle_json_decode_error(e: Exception, current_user_id: int, endpoint: str) -> None:
    """
    Behandelt JSON-Dekodierungsfehler.

    Args:
        e (Exception): Die Ausnahme, die ausgelöst wurde.
        current_user_id (int): Die ID des aktuellen Benutzers.
        endpoint (str): Der Endpunkt, auf den zugegriffen wird.
    """
    logging_error = schemas.LoggingSchema(
        user_id=current_user_id,
        endpoint=endpoint,
        method="GET",
        message=f"Fehler beim Parsen der Log-Zeile: {str(e)}",
        success=False
    )
    logger.error(logging_error.dict())


@router.get("/dateUserOverview", status_code=status.HTTP_200_OK)
async def get_users(current_user: models.Nutzer = Depends(oauth.get_current_user),
                    db: AsyncSession = Depends(database.get_db_async)):
    """
    Liefert eine Zusammenfassung der gestern und heute registrierten Benutzer.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        dict: Ein Wörterbuch mit der Anzahl der gestern und heute registrierten Benutzer, aufgeschlüsselt nach Rollen.

    Raises:
        HTTPException: Wenn es ein Problem beim Abrufen der Daten gibt.
    """
    try:
        await check_admin_role(current_user, method="GET", endpoint="/dateUserOverview")
        today = date.today()
        yesterday = today - timedelta(days=1)
        start_of_yesterday = datetime.combine(yesterday, datetime.min.time())
        start_of_today = datetime.combine(today, datetime.min.time())
        end_of_today = start_of_today + timedelta(days=1)
        try:
            yesterday_stmt = select(models.Nutzer.rolle).where(
                (models.Nutzer.created_at >= start_of_yesterday) &
                (models.Nutzer.created_at < start_of_today)
            )
            yesterday_result = await db.execute(yesterday_stmt)
            today_stmt = select(models.Nutzer.rolle).where(
                (models.Nutzer.created_at >= start_of_today) &
                (models.Nutzer.created_at < end_of_today)  # Remove this condition if you want up to the current time
            )
            today_result = await db.execute(today_stmt)
            yesterday_results = [x[0] for x in yesterday_result.all()]
            today_results = [x[0] for x in today_result.all()]
            yesterday_counter = Counter(yesterday_results)
            today_counter = Counter(today_results)
            formatted_data = {0: yesterday_counter, 1: today_counter}
            logging_info = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/admin/userOverview",
                method="GET",
                message="Rollenübersicht erfolgreich abgerufen",
                success=True
            )
            logger.info(logging_info.dict())
            return formatted_data

        except exc.IntegrityError as e:
            if Settings.DEV:
                msg = f"Error beim User Abfragen: {e.orig}"
                logging_msg = msg
            else:
                logging_msg = f"Error beim User Abfragen: {e.orig}"
                msg = "Es gab einen Fehler bei der user Abfrage."
            logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/users/", method="GET",
                                                message=logging_msg, success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/admin/userOverview",
            method="GET",
            message=f"Fehler beim Abrufen der Rollenübersicht: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Fehler beim Abrufen der Rollenübersicht")


@router.get("/logOverview", status_code=status.HTTP_200_OK,
            response_model=List[schemas.BarChartData])
async def get_log_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> List[schemas.BarChartData]:
    """
    Gibt einen Überblick über die Protokollaktivitäten nach Datum.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.

    Returns:
        List[schemas.BarChartData]: Eine nach Datum zusammengefasste Liste von Protokollaktivitäten.

    Raises:
        HTTPException: Wenn es ein Problem mit dem Zugriff auf die Protokolldatei oder der Verarbeitung
                       ihres Inhalts gibt.
    """
    await check_admin_role(current_user, method="GET", endpoint="/logOverview")

    log_file_path = Path("logs/server.log")
    await check_log_file_existence(log_file_path, current_user.user_id, "/admin/logOverview")

    activity_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                date_str = log_entry["timestamp"].split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                activity_count[date] += 1
            except (IndexError, ValueError) as e:
                handle_json_decode_error(e, current_user.user_id, "/admin/logOverview")
                continue

    formatted_data = [{"date": date, "value": count} for date, count in activity_count.items()]
    logging_obj = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/admin/logOverview",
        method="GET",
        message="Log-Übersicht erfolgreich abgerufen",
        success=True)
    logger.info(logging_obj.dict())
    return formatted_data


@router.get("/endpointOverview", status_code=status.HTTP_200_OK, response_model=List[Dict[str, Any]])
async def get_endpoint_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> List[Dict[str, Any]]:
    """
    Gibt einen Überblick über die Endpunktaktivitäten, zusammengefasst nach Datum.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.

    Returns:
        List[Dict[str, Any]]: Eine Liste von Endpunktaktivitäten, die jeweils die Endpunkt-ID und Datenpunkte für
        die Aktivität nach Datum enthalten.

    Raises:
        HTTPException: Wenn es ein Problem mit dem Zugriff auf die Protokolldatei oder der Verarbeitung ihres Inhalts gibt.
    """
    await check_admin_role(current_user, method="GET", endpoint="/endpointOverview")
    log_file_path = Path("logs/server.log")
    await check_log_file_existence(log_file_path, current_user.user_id, "/admin/endpointOverview")

    endpoint_activity = defaultdict(Counter)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                date_str = log_entry["timestamp"].split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                endpoint = log_entry["endpoint"]
                endpoint_activity[endpoint][date] += 1
            except (KeyError, json.JSONDecodeError) as e:
                handle_json_decode_error(e, current_user.user_id, "/admin/endpointOverview")
                continue  # Ungültige Zeilen werden automatisch übersprungen

    formatted_data = [{"id": endpoint, "data":
        [{"x": date, "y": count} for date, count in dates.items()]} for endpoint, dates in endpoint_activity.items()]
    logging_info = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/admin/endpointOverview",
        method="GET",
        message="Endpoint-Übersicht erfolgreich abgerufen",
        success=True
    )
    logger.info(logging_info.dict())
    return formatted_data


@router.get("/successOverview", status_code=status.HTTP_200_OK,
            response_model=Dict[str, List[Dict[str, Union[str, int]]]])
async def get_success_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> Dict[str, List[Dict[str, Union[str, int]]]]:
    """
    Verschafft einen Überblick über erfolgreiche und fehlgeschlagene Anfragen.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.

    Returns:
        Dict[str, List[Dict[str, Union[str, int]]]]: Ein Wörterbuch mit separaten Listen von erfolgreichen
                                                     und fehlgeschlagenen Anfragen, zusammengefasst nach Datum.

    Raises:
        HTTPException: Wenn es ein Problem mit dem Zugriff auf die Protokolldatei oder der Verarbeitung ihres Inhalts gibt.
    """
    await check_admin_role(current_user, method="GET", endpoint="/successOverview")
    log_file_path = Path("logs/server.log")
    await check_log_file_existence(log_file_path, current_user.user_id, "/admin/successOverview")

    success_activity = defaultdict(lambda: {'success': 0, 'fail': 0})
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                date_str = log_entry["timestamp"].split(" ")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                success_flag = log_entry["success"]
                if success_flag:
                    success_activity[date]['success'] += 1
                else:
                    success_activity[date]['fail'] += 1
            except json.JSONDecodeError as e:
                handle_json_decode_error(e, current_user.user_id, "/admin/successOverview")
                continue  # Ungültige Zeilen werden automatisch übersprungen

    success_data = [{"date": date, "value": data['success']} for date, data in success_activity.items()]
    fail_data = [{"date": date, "value": data['fail']} for date, data in success_activity.items()]

    logging_info = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/admin/successOverview",
        method="GET",
        message="Erfolgsübersicht erfolgreich abgerufen",
        success=True
    )
    logger.info(logging_info.dict())

    return {"success": success_data, "fail": fail_data}


@router.get("/registrationOverview", status_code=status.HTTP_200_OK, response_model=List[schemas.BarChartData])
async def get_registration_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> List[schemas.ChartData]:
    """
    Gibt einen Überblick über die Benutzerregistrierungen nach Datum.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.

    Returns:
        List[schemas.ChartData]: Eine Liste der Anzahl der Benutzerregistrierungen, zusammengefasst nach Datum.

    Raises:
        HTTPException: Wenn es ein Problem mit dem Zugriff auf die Protokolldatei oder der Verarbeitung
                       ihres Inhalts gibt.
    """
    await check_admin_role(current_user, method="GET", endpoint="/registrationOverview")
    log_file_path = Path("logs/server.log")
    await check_log_file_existence(log_file_path, current_user.user_id, "/admin/registrationOverview")

    registration_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                if log_entry.get("message") == "User registriert":
                    date_str = log_entry["timestamp"].split(" ")[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")

                    registration_count[date] += 1
            except(IndexError, json.JSONDecodeError) as e:
                handle_json_decode_error(e, current_user.user_id, "/admin/registrationOverview")
                continue

    formatted_data = [{"date": date, "value": count} for date, count in registration_count.items()]
    logging_info = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/admin/registrationOverview",
        method="GET",
        message="Registrierungsübersicht erfolgreich abgerufen",
        success=True
    )
    logger.info(logging_info.dict())
    return formatted_data


@router.get("/loginOverview", status_code=status.HTTP_200_OK,
            response_model=List[schemas.BarChartData])
async def get_login_overview(current_user: models.Nutzer = Depends(oauth.get_current_user)) \
        -> List[schemas.ChartData]:
    """
    Übersicht der Benutzeranmeldungen nach Datum.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.

    Returns:
        List[schemas.ChartData]: Eine Liste der Anzahl der Benutzeranmeldungen, zusammengefasst nach Datum.

    Raises:
        HTTPException: Wenn es ein Problem mit dem Zugriff auf die Protokolldatei oder der Verarbeitung ihres Inhalts gibt.
    """
    await check_admin_role(current_user, method="GET", endpoint="/loginOverview")
    log_file_path = Path("logs/server.log")
    await check_log_file_existence(log_file_path, current_user.user_id, "/admin/loginOverview")

    login_count = defaultdict(int)
    with open(log_file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                if log_entry.get("message") == "User eingeloggt":
                    date_str = log_entry["timestamp"].split(" ")[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
                    login_count[date] += 1
            except(IndexError, json.JSONDecodeError) as e:
                handle_json_decode_error(e, current_user.user_id, "/admin/loginOverview")
                continue

    formatted_data = [{"date": date, "value": count} for date, count in login_count.items()]
    logging_info = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/admin/loginOverview",
        method="GET",
        message="Login-Übersicht erfolgreich abgerufen",
        success=True
    )
    logger.info(logging_info.dict())
    return formatted_data


@router.get("/userOverview", status_code=status.HTTP_200_OK, response_model=List[schemas.PieChartData])
async def get_user_overview(current_user: models.Nutzer = Depends(oauth.get_current_user),
                            db: AsyncSession = Depends(database.get_db_async)) -> List[schemas.PieChartData]:
    """
    Verschafft einen Überblick über die Benutzer, kategorisiert nach Rolle.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext stammt.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        List[schemas.PieChartData]: Eine Liste von Benutzerrollen und deren Anzahl.

    Raises:
        HTTPException: Wenn es ein Problem bei der Abfrage der Datenbank oder der Verarbeitung der Daten gibt.
    """
    try:
        await check_admin_role(current_user, method="GET", endpoint="/userOverview")
        stmt = (
            select(models.Nutzer)
        )
        try:
            result = await db.execute(stmt)
            users = result.all()
            users_role = [
                user[0].rolle.name if user[0].rolle is not None else "Unknown"
                for user in users]

            role_count = Counter(users_role)

            formatted_data = [{"id": role, "label": role, "value": count} for role, count in role_count.items()]
            logging_info = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/admin/userOverview",
                method="GET",
                message="Rollenübersicht erfolgreich abgerufen",
                success=True
            )
            logger.info(logging_info.dict())
            return formatted_data

        except exc.IntegrityError as e:
            if Settings.DEV:
                msg = f"Error beim User Abfragen: {e.orig}"
                logging_msg = msg
            else:
                logging_msg = f"Error beim User Abfragen: {e.orig}"
                msg = "Es gab einen Fehler bei der user Abfrage."
            logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/users/", method="GET",
                                                message=logging_msg, success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/admin/userOverview",
            method="GET",
            message=f"Fehler beim Abrufen der Rollenübersicht: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Fehler beim Abrufen der Rollenübersicht")


@router.get("/logs", status_code=status.HTTP_200_OK, response_model=List[schemas.LogEntry])
async def get_logs(current_user: models.Nutzer = Depends(oauth.get_current_user)) -> List[schemas.LogEntry]:
    """
    Alle Protokolleinträge abrufen.

    Args:
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext bezogen wird.

    Returns:
        List[schemas.LogEntry]: Eine Liste von Protokolleinträgen.

    Raises:
        HTTPException: Wenn es ein Problem mit dem Zugriff oder der Verarbeitung der Protokolldatei gibt.
    """
    await check_admin_role(current_user, method="GET", endpoint="/logs")
    try:
        log_file_path = Path("logs/server.log")

        if not log_file_path.exists() or log_file_path.stat().st_size == 0:
            logging_error = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint="/admin/logs",
                method="GET",
                message="Log-Datei existiert nicht oder ist leer",
                success=False
            )
            logger.error(logging_error.dict())

        logs = []
        with open(log_file_path, 'r') as file:
            for (ind, line) in enumerate(file):
                try:
                    log_entry = json.loads(line)
                    log_entry["log_id"] = ind
                    try:
                        schemas.LogEntry.from_orm(log_entry)
                        logs.append(log_entry)
                    except Exception as e:
                        logging_error = schemas.LoggingSchema(
                            user_id=current_user.user_id,
                            endpoint="/admin/logs",
                            method="GET",
                            message=f"Validierungsfehler: {str(e)}",
                            success=False
                        )
                        logger.error(logging_error.dict())
                        continue
                except json.JSONDecodeError as e:
                    handle_json_decode_error(e, current_user.user_id, "/admin/logs")
                    continue

        return logs
    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/admin/logs",
            method="GET",
            message=f"Fehler beim Abrufen der Logs: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen der Logs")


@router.post("/kalendereintrag", status_code=status.HTTP_201_CREATED)
async def create_kalender_eintrag(eintrag: schemas.KalenderEintragCreate,
                                  db: AsyncSession = Depends(database.get_db_async),
                                  current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Erstellt einen neuen Kalendereintrag.

    Args:
        eintrag (schemas.KalenderEintragCreate): Die Daten für den neuen Kalendereintrag.
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext bezogen wird.

    Returns:
        schemas.KalenderEintrag: Der neu erstellte Kalendereintrag.

    Raises:
        HTTPException: Wenn es ein Problem bei der Erstellung des Eintrags in der Datenbank gibt.
    """
    try:
        if isinstance(eintrag.start, str):
            if "T" in eintrag.start:
                eintrag.start = (datetime.strptime(eintrag.start, "%Y-%m-%dT%H:%M:%S%z")).replace(tzinfo=None)
            else:
                eintrag.start = datetime.strptime(eintrag.start, '%Y-%m-%d').date()

        if isinstance(eintrag.ende, str):
            if "T" in eintrag.ende:
                eintrag.ende = datetime.strptime(eintrag.ende, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
            else:
                eintrag.ende = datetime.strptime(eintrag.ende, '%Y-%m-%d').date()
        db_eintrag = models.Kalendereintrag(**eintrag.dict())
        db_eintrag.user_id = current_user.user_id
        db.add(db_eintrag)
        await db.commit()
        await db.refresh(db_eintrag)

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kalendereintrag/",
            method="POST",
            message="Neuer Kalendereintrag erstellt",
            success=True
        )
        logger.info(logging_obj.dict())

        return db_eintrag
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kalendereintrag",
            method="POST",
            message=f"Fehler beim Erstellen eines Kalendereintrags: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kalendereintrag", status_code=status.HTTP_200_OK, response_model=List[schemas.KalenderEintragResponse])
async def get_kalendereintraege(db: AsyncSession = Depends(database.get_db_async),
                                current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft alle Kalendereinträge ab.

    Args:
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das aus dem aktuellen Anfragekontext erhaltene Benutzerobjekt.

    Returns:
        List[schemas.KalenderEintrag]: Eine Liste von Kalendereinträgen.

    Raises:
        HTTPException: Wenn es ein Problem beim Abrufen von Daten aus der Datenbank gibt.
    """

    try:
        stmt = select(models.Kalendereintrag).where(models.Kalendereintrag.user_id == current_user.user_id)
        result = await db.execute(stmt)
        eintraege = result.scalars().all()

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kalendereintrag/",
            method="GET",
            message="Alle Kalendereinträge erfolgreich abgerufen",
            success=True
        )
        logger.info(logging_obj.dict())

        return [{
            "beschreibung": eintrag.beschreibung,
            "start": str(eintrag.start),
            "ende": str(eintrag.ende),
            "allDay": eintrag.allDay,
        } for eintrag in eintraege]

    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/kalendereintrag/",
            method="GET",
            message=f"Fehler beim Abrufen von Kalendereinträgen: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kalendereintrag/{eintrag_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.KalenderEintrag)
async def get_kalendereintrag(eintrag_id: int, db: AsyncSession = Depends(database.get_db_async),
                              current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft einen bestimmten Kalendereintrag anhand seiner ID ab.

    Args:
        eintrag_id (int): Die ID des abzurufenden Kalendereintrags.
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext bezogen wird.

    Returns:
        schemas.KalenderEintrag: Der angeforderte Kalendereintrag.

    Raises:
        HTTPException: Wenn der Eintrag nicht gefunden wird oder es ein Problem mit der Datenbankabfrage gibt.
    """

    try:
        db_eintrag = await db.get(models.Kalendereintrag, eintrag_id)
        if db_eintrag is None:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/kalendereintrag/{eintrag_id}",
                method="GET",
                message=f"Kalendereintrag {eintrag_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Kalendereintrag nicht gefunden")

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kalendereintrag/{eintrag_id}",
            method="GET",
            message=f"Kalendereintrag {eintrag_id} erfolgreich abgerufen",
            success=True
        )
        logger.info(logging_obj.dict())

        return db_eintrag
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kalendereintrag/{eintrag_id}",
            method="GET",
            message=f"Fehler beim Abrufen des Kalendereintrags {eintrag_id}: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/kalendereintrag/{eintrag_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.KalenderEintrag)
async def update_kalendereintrag(eintrag_id: int, eintrag_data: schemas.KalenderEintragCreate,
                                 db: AsyncSession = Depends(database.get_db_async),
                                 current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Aktualisiert einen bestimmten Kalendereintrag anhand seiner ID.

    Args:
        eintrag_id (int): Die ID des zu aktualisierenden Kalendereintrags.
        eintrag_data (schemas.KalenderEintragCreate): Die aktualisierten Daten für den Kalendereintrag.
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext bezogen wird.

    Returns:
        schemas.KalenderEintrag: Der aktualisierte Kalendereintrag.

    Raises:
        HTTPException: Wenn der Eintrag nicht gefunden wird oder es ein Problem mit der Aktualisierung des Datenbankeintrags gibt.
    """
    try:
        db_eintrag = await db.get(models.Kalendereintrag, eintrag_id)
        if db_eintrag is None:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/kalendereintrag/{eintrag_id}",
                method="PUT",
                message=f"Kalendereintrag {eintrag_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Kalendereintrag nicht gefunden")

        for key, value in eintrag_data.dict().items():
            setattr(db_eintrag, key, value)

        await db.commit()
        await db.refresh(db_eintrag)

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kalendereintrag/{eintrag_id}",
            method="PUT",
            message=f"Kalendereintrag {eintrag_id} aktualisiert",
            success=True
        )
        logger.info(logging_obj.dict())

        return db_eintrag
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kalendereintrag/{eintrag_id}",
            method="PUT",
            message=f"Fehler beim Aktualisieren des Kalendereintrags {eintrag_id}: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/kalendereintrag/{eintrag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kalendereintrag(eintrag_id: int, db: AsyncSession = Depends(database.get_db_async),
                                 current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Löscht einen bestimmten Kalendereintrag anhand seiner ID.

    Args:
        eintrag_id (int): Die ID des zu löschenden Kalendereintrags.
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anfragekontext bezogen wird.

    Returns:
        Antwort: Eine leere Antwort mit dem HTTP-Statuscode 204 als Hinweis auf eine erfolgreiche Löschung.

    Raises:
        HTTPException: Wenn der Eintrag nicht gefunden wird oder es ein Problem beim Löschen des Datenbankeintrags gibt.
    """
    await check_admin_role(current_user, "DELETE", f"/kalendereintrag/{eintrag_id}")
    try:
        db_eintrag = await db.get(models.Kalendereintrag, eintrag_id)
        if db_eintrag is None:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/kalendereintrag/{eintrag_id}",
                method="DELETE",
                message=f"Kalendereintrag {eintrag_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Kalendereintrag nicht gefunden")

        await db.delete(db_eintrag)
        await db.commit()

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kalendereintrag/{eintrag_id}",
            method="PUT",
            message=f"Kalendereintrag {eintrag_id} gelöscht",
            success=True
        )
        logger.info(logging_obj.dict())

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/kalendereintrag/{eintrag_id}",
            method="DELETE",
            message=f"Fehler beim Löschen des Kalendereintrags {eintrag_id}: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download_reports_dashboard", status_code=status.HTTP_200_OK)
async def download_reports_dashboard(db: AsyncSession = Depends(database.get_db_async),
                                     current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ladet einen Dashboard-Bericht herunter, der verschiedene Metriken zusammenfasst, darunter die Gesamtzahl der Nutzer,
    Backend-Aufrufe, neue Energie- und PV-Anfragen sowie die Nutzerzahlen nach Rolle.

    Args:
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Abfragekontext abgerufen wird;
        es wird erwartet, dass es sich um einen Administrator handelt.

    Returns:
        StreamingResponse: Eine CSV-Datei mit den zusammengefassten Dashboard-Metriken.

    Raises:
        HTTPException: Wenn während der Berichtserstellung ein interner Serverfehler auftritt.
    """
    await check_admin_role(current_user, "GET", "/download_reports_dashboard")
    try:
        # Gesamtanzahl Nutzer
        total_users = await db.execute(select(func.count(models.Nutzer.user_id)))

        # Anzahl Backend Aufrufe 
        backend_calls = 0
        with open("logs/server.log", "r") as file:
            for line in file:
                log_entry = json.loads(line)
                if log_entry.get("level") == "INFO":
                    backend_calls += 1
        # Neue Kontaktanfragen für Energieausweise und PVAnlagen
        new_energy_requests = await db.execute(select(func.count(models.Energieausweise.energieausweis_id)).where(
            models.Energieausweise.ausweis_status == "AnfrageGestellt"))
        new_pv_requests = await db.execute(
            select(func.count(models.PVAnlage.anlage_id)).where(models.PVAnlage.prozess_status == "AnfrageGestellt"))

        # Anzahl der Nutzer nach Rollen
        admin_count = await db.execute(select(func.count(models.Nutzer.user_id)).where(models.Nutzer.rolle == "Admin"))
        solarteure_count = await db.execute(
            select(func.count(models.Nutzer.user_id)).where(models.Nutzer.rolle == "Solarteure"))
        energieberatende_count = await db.execute(
            select(func.count(models.Nutzer.user_id)).where(models.Nutzer.rolle == "Energieberatende"))
        netzbetreiber_count = await db.execute(
            select(func.count(models.Nutzer.user_id)).where(models.Nutzer.rolle == "Netzbetreiber"))
        haushalte_count = await db.execute(
            select(func.count(models.Nutzer.user_id)).where(models.Nutzer.rolle == "Haushalte"))

        # Erstellen der CSV-Datei
        output = io.StringIO()
        writer = csv.writer(output)

        # Schreiben der Kopfzeilen
        header = ["Kategorie", "Anzahl"]
        writer.writerow(header)

        # Schreiben der Daten
        writer.writerow(["Gesamtanzahl Nutzer", total_users.scalar()])
        writer.writerow(["Backend Aufrufe", backend_calls])
        writer.writerow(["Neue Energieanfragen", new_energy_requests.scalar()])
        writer.writerow(["Neue PV Anfragen", new_pv_requests.scalar()])
        writer.writerow(["Anzahl Admins", admin_count.scalar()])
        writer.writerow(["Anzahl Solarteure", solarteure_count.scalar()])
        writer.writerow(["Anzahl Energieberatende", energieberatende_count.scalar()])
        writer.writerow(["Anzahl Netzbetreiber", netzbetreiber_count.scalar()])
        writer.writerow(["Anzahl Haushalte", haushalte_count.scalar()])

        output.seek(0)  # Zurück zum Anfang der Datei
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)


@router.get("/download_reports_vertrag", status_code=status.HTTP_200_OK)
async def download_reports_vertrag(db: AsyncSession = Depends(database.get_db_async),
                                   current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ladet einen Bericht über alle Verträge im CSV-Format herunter.

    Args:
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das aus dem aktuellen Anfragekontext erhaltene Benutzerobjekt, bei dem es sich
        voraussichtlich um einen Administrator handelt.

    Returns:
        StreamingResponse: Eine CSV-Datei mit Details zu allen Verträgen.

    Raises:
        HTTPException: Wenn während der Berichtserstellung ein interner Serverfehler auftritt.
    """
    await check_admin_role(current_user, "GET", "/download_reports_vertrag")

    try:
        vertraege = await db.execute(select(models.Vertrag))

        # Erstellen der CSV-Datei
        output = io.StringIO()
        writer = csv.writer(output)

        # Schreiben der Kopfzeilen entsprechend der Tabelle Vertrag
        header = ["vertrag_id", "user_id", "tarif_id", "beginn_datum", "end_datum", "netzbetreiber_id",
                  "jahresabschlag", "vertragstatus"]
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
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=vertrag_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)


@router.get("/download_reports_rechnungen", status_code=status.HTTP_200_OK)
async def download_reports_rechnung(db: AsyncSession = Depends(database.get_db_async),
                                    current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ladet einen Bericht mit allen Rechnungen im CSV-Format herunter.

    Args:
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das Benutzerobjekt, das aus dem aktuellen Anforderungskontext abgerufen wird;
        es wird erwartet, dass es sich um einen Administrator handelt.

    Returns:
        StreamingResponse: Eine CSV-Datei mit Details zu allen Rechnungen.

    Raises:
        HTTPException: Wenn während der Berichtserstellung ein interner Serverfehler auftritt.
    """
    await check_admin_role(current_user, "GET", "/download_reports_rechnungen")

    try:
        rechnungen = await db.execute(select(models.Rechnungen))

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
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=rechnungen_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)


@router.get("/download_reports_energieausweise", status_code=status.HTTP_200_OK)
async def download_reports_eausweis(db: AsyncSession = Depends(database.get_db_async),
                                    current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ladet einen Bericht über alle Energieausweise im CSV-Format herunter.

    Args:
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das aus dem aktuellen Anfragekontext erhaltene Benutzerobjekt, bei dem es sich
        voraussichtlich um einen Administrator handelt.

    Returns:
        StreamingResponse: Eine CSV-Datei mit Details zu allen Energieausweisen.

    Raises:
        HTTPException: Wenn während der Berichtserstellung ein interner Serverfehler auftritt.
    """
    await check_admin_role(current_user, "GET", "/download_reports_energieausweise")

    try:
        # Wählen Sie alle Energieausweise aus, wenn der Nutzer Admin ist
        energieausweise = await db.execute(select(models.Energieausweise))

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
                ausweis.ausweis_status.value  # Achten Sie auf den Enum-Typ hier
            ])

        output.seek(0)  # Zurück zum Anfang der Datei
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=energieausweise_report.csv"})

    except Exception as e:
        logging_error = {"message": f"Serverfehler: {str(e)}", "trace": traceback.format_exc()}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=logging_error)


@router.put("/activate-user/{user_id}", status_code=status.HTTP_200_OK)
async def activate_user(user_id: int, db: AsyncSession = Depends(database.get_db_async),
                        current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Aktiviert ein Benutzerkonto.

    Args:
        user_id (int): Die ID des zu aktivierenden Benutzerkontos.
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das aus dem aktuellen Anfragekontext erhaltene Benutzerobjekt.

    Returns:
        dict: Eine Nachricht, die den Erfolg der Operation bestätigt.
    """
    await check_admin_role(current_user, "PUT", "/activate-user")
    user_to_activate = await db.get(models.Nutzer, user_id)
    if user_to_activate:
        user_to_activate.is_active = True
        await db.commit()
        return {"message": f"User with ID {user_id} has been activated."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden.")


@router.put("/deactivate-user/{user_id}", status_code=status.HTTP_200_OK)
async def deactivate_user(user_id: int, db: AsyncSession = Depends(database.get_db_async),
                          current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Deaktiviert ein Benutzerkonto.

    Args:
        user_id (int): Die ID des zu deaktivierenden Benutzerkontos.
        db (AsyncSession): Die Datenbanksitzung.
        current_user (models.Nutzer): Das aus dem aktuellen Anfragekontext erhaltene Benutzerobjekt.

    Returns:
        dict: Eine Nachricht, die den Erfolg der Operation bestätigt.
    """
    await check_admin_role(current_user, "PUT", "/deactivate-user")
    user_to_deactivate = await db.get(models.Nutzer, user_id)
    if user_to_deactivate:
        user_to_deactivate.is_active = False
        await db.commit()
        return {"message": f"User with ID {user_id} has been deactivated."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden.")
