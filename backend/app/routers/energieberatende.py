from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from typing import List, Union
from app import models, schemas, database, oauth, types
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.schemas import LoggingSchema

router = APIRouter(prefix="/energieberatende", tags=["Energieberatende"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_energieberatende_role(current_user: models.Nutzer, method: str, endpoint: str):
    """
    Prüft, ob der aktuelle Benutzer die Rolle eines Energieberaters hat.

    Args:
        current_user (models.Nutzer): Das aktuelle Benutzerobjekt.
        method (str): Die HTTP-Methode der Anfrage.
        endpoint (str): Der Endpunkt, auf den zugegriffen wird.

    Raises:
        HTTPException: Wenn der aktuelle Benutzer nicht die Rolle 'Energieberater' hat.
    """
    if current_user.rolle != models.Rolle.Energieberatende:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Energieberatender",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Nur Energieberatende haben Zugriff auf diese Daten")


def log_and_raise_http_exception(user_id: int, endpoint: str, method: str, message: str, success: bool,
                                 status_code: int, detail: str):
    """
    Protokolliert eine Fehler- oder Informationsmeldung und löst eine HTTPException aus.

    Args:
        user_id (int): Die ID des aktuellen Benutzers.
        endpoint (str): Der Endpunkt, auf den zugegriffen wird.
        method (str): Die HTTP-Methode der Anfrage.
        message (str): Die zu protokollierende Nachricht.
        success (bool): Gibt an, ob der Vorgang erfolgreich war.
        status_code (int): Der HTTP-Statuscode, der zurückgegeben werden soll.
        detail (str): Die Detailmeldung, die in die HTTPException aufgenommen werden soll.

    Raises:
        HTTPException: Mit dem angegebenen Statuscode und der Detailmeldung.
    """
    logging_obj = schemas.LoggingSchema(
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        message=message,
        success=success
    )
    logger.error(logging_obj.dict()) if not success else logger.info(logging_obj.dict())
    raise HTTPException(status_code=status_code, detail=detail)


@router.get("/anfragen", response_model=List[schemas.PVSolarteuerResponse])
async def get_anfragen(
        prozess_status: List[types.ProzessStatus] = Query(None),
        current_user: models.Nutzer = Depends(oauth.get_current_user),
        db: AsyncSession = Depends(database.get_db_async)
):
    """
    Ruft Anfragen auf der Grundlage des Prozessstatus ab.

    Args:
        prozess_status (Optional[Liste[types.ProzessStatus]]): Der Prozessstatus, nach dem die Anfragen gefiltert werden sollen.
        current_user (models.Nutzer): Der aktuelle Benutzer, injizierte Abhängigkeit von OAuth.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        List[schemas.PVSolarteuerResponse]: Eine Liste von Anfragen, die dem angegebenen Prozessstatus entsprechen.

    Raises:
        HTTPException: Wenn ein Fehler beim Abrufen von Anfragen aus der Datenbank auftritt.
    """
    await check_energieberatende_role(current_user, "GET", "/angebote")

    try:
        query = build_anfragen_query(prozess_status, current_user)
        result = await db.execute(query)
        anfragen = result.all()

        if not anfragen:
            return []

        return format_anfragen_response(anfragen)

    except SQLAlchemyError as e:
        log_and_raise_http_exception(
            user_id=current_user.user_id,
            endpoint="/angebote",
            method="GET",
            message=f"Fehler beim Abrufen der Angebote: {e}",
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen der Angebote: {e}"
        )


def build_anfragen_query(prozess_status, current_user):
    """
    Erstellt die Abfrage zum Abrufen von Anfragen auf der Grundlage des Prozessstatus und der Rolle des aktuellen Benutzers.

    Args:
        prozess_status (Optional[Liste[types.ProzessStatus]]): Der Prozessstatus, nach dem die Abfragen gefiltert werden sollen.
        current_user (models.Nutzer): Der aktuelle Benutzer.

    Returns:
        str: Die SQL-Abfrage als String.
    """
    if prozess_status and prozess_status[0] == types.ProzessStatus.AusweisAngefordert and len(prozess_status) == 1:
        return (select(models.PVAnlage, models.Nutzer, models.Adresse, None)
                .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                .where(models.PVAnlage.prozess_status == models.ProzessStatus.AusweisAngefordert))
    else:
        query = (select(models.PVAnlage, models.Nutzer, models.Adresse, models.Energieausweise)
                 .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                 .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                 .join(models.Energieausweise,
                       models.PVAnlage.energieausweis_id == models.Energieausweise.energieausweis_id))

        if prozess_status:
            query = query.where((models.PVAnlage.prozess_status.in_(prozess_status))
                                & (models.Energieausweise.energieberater_id == current_user.user_id))
        return query


def format_anfragen_response(anfragen):
    """
    Formatiert die Anfragen in eine Liste von Wörterbüchern, die für die JSON-Serialisierung geeignet sind.

    Args:
        anfragen (Liste): Die Liste der Abfragen, die aus der Datenbank geholt wurden.

    Returns:
        List[dict]: Eine Liste von Abfragen, die als Wörterbuch formatiert sind.
    """
    return [{
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
    } for angebot, nutzer, adresse, ausweis in anfragen]


def build_get_anfrage_query(anlage_id):
    """
    Erstellt die SQL-Abfrage zum Abrufen einer bestimmten Anfrage anhand ihrer ID.

    Args:
        anlage_id (int): Die ID der Anfrage.

    Returns:
        str: Die SQL-Abfrage als String.
    """
    return (select(models.PVAnlage, models.Nutzer, models.Adresse, models.Energieausweise)
            .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
            .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
            .join(models.Energieausweise, models.PVAnlage.energieausweis_id == models.Energieausweise.energieausweis_id)
            .where(models.PVAnlage.anlage_id == anlage_id))


def format_anfrage_response(angebot):
    """
    Formatiert eine einzelne Anfrage in ein für die JSON-Serialisierung geeignetes Wörterbuch.

    Args:
        angebot (Tupel): Die aus der Datenbank geholten Anfragedaten.

    Returns:
        dict: Die als Wörterbuch formatierte Anfrage.
    """
    if angebot[0].prozess_status == models.ProzessStatus.Genehmigt:
        response = {
            "anlage_id": angebot[0].anlage_id,
            "haushalt_id": angebot[0].haushalt_id,
            "solarteur_id": angebot[0].solarteur_id,
            "modultyp": angebot[0].modultyp,
            "kapazitaet": angebot[0].kapazitaet,
            "installationsflaeche": angebot[0].installationsflaeche,
            "installationsdatum": str(angebot[0].installationsdatum),
            "nvpruefung_status": angebot[0].nvpruefung_status,
            "modulanordnung": angebot[0].modulanordnung,
            "kabelwegfuehrung": angebot[0].kabelwegfuehrung,
            "montagesystem": angebot[0].montagesystem,
            "schattenanalyse": angebot[0].schattenanalyse,
            "wechselrichterposition": angebot[0].wechselrichterposition,
            "prozess_status": angebot[0].prozess_status,
            "vorname": angebot[1].vorname,
            "nachname": angebot[1].nachname,
            "email": angebot[1].email,
            "strasse": angebot[2].strasse,
            "hausnummer": angebot[2].hausnummer,
            "plz": angebot[2].plz,
            "stadt": angebot[2].stadt,
            "energieausweis_id": angebot[3].energieausweis_id,
        }

        return response

    return {
        "anlage_id": angebot[0].anlage_id,
        "haushalt_id": angebot[0].haushalt_id,
        "prozess_status": angebot[0].prozess_status,
        "vorname": angebot[1].vorname,
        "nachname": angebot[1].nachname,
        "email": angebot[1].email,
        "strasse": angebot[2].strasse,
        "hausnummer": angebot[2].hausnummer,
        "plz": angebot[2].plz,
        "stadt": angebot[2].stadt,
        "energieausweis_id": angebot[3].energieausweis_id,
    }


@router.get("/anfragen/{anlage_id}")
async def get_anfrage(anlage_id: int, current_user: models.Nutzer = Depends(oauth.get_current_user),
                      db: AsyncSession = Depends(database.get_db_async)):
    """
    Ruft eine bestimmte Anfrage anhand ihrer ID ab.

    Args:
        anlage_id (int): Die ID der abzurufenden Anfrage.
        current_user (models.Nutzer): Der aktuelle Benutzer, injizierte Abhängigkeit von OAuth.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        schemas.PVAnlageResponse: Die Anfrage, die mit der angegebenen ID übereinstimmt.

    Raises:
        HTTPException: Wenn die Anfrage nicht gefunden werden kann oder ein Datenbankfehler vorliegt.
    """
    await check_energieberatende_role(current_user, "GET", f"/angebote/{anlage_id}")

    try:
        stmt = build_get_anfrage_query(anlage_id)
        result = await db.execute(stmt)
        angebot = result.first()

        if not angebot:
            log_and_raise_http_exception(
                user_id=current_user.user_id,
                endpoint=f"/angebote/{anlage_id}",
                method="GET",
                message="Angebot nicht gefunden",
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Anfrage {anlage_id} nicht gefunden"
            )

        return format_anfrage_response(angebot)

    except SQLAlchemyError as e:
        log_and_raise_http_exception(
            user_id=current_user.user_id,
            endpoint=f"/angebote/{anlage_id}",
            method="GET",
            message=f"Fehler beim Abrufen des Angebots: {e}",
            success=False,
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Fehler beim Abrufen des Angebots: {e}"
        )


async def get_latest_massnahmen_for_haushalt(haushalt_id: int, db: AsyncSession):
    """
    Ruft die neueste Energieeffizienzmaßnahme für einen bestimmten Haushalt ab.

    Args:
        haushalt_id (int): Der eindeutige Bezeichner für den Haushalt.
        db (AsyncSession): Die Datenbanksitzung für die Ausführung asynchroner Datenbankoperationen.

    Returns:
        models.Energieeffizienzmassnahmen: Die letzte Energieeffizienzmassnahme für den Haushalt.

    Raises:
        NoResultFound: Wenn keine Maßnahmen für den Haushalt gefunden werden.
    """
    massnahmen_query = (select(models.Energieeffizienzmassnahmen)
                        .where(models.Energieeffizienzmassnahmen.haushalt_id == haushalt_id)
                        .order_by(models.Energieeffizienzmassnahmen.created_at.desc())
                        .limit(1))
    massnahmen_result = await db.execute(massnahmen_query)
    return massnahmen_result.scalars().first()


async def create_new_rechnung(empfaenger_id: int, steller_id: int, kosten: float, db: AsyncSession):
    """
    Erzeugt ein neues Rechnung-Objekt und fügt es der Datenbank hinzu.

    Args:
        empfaenger_id (int): Die ID des Empfängers (Haushalt) der Rechnung.
        steller_id (int): Die ID des Ausstellers (Energieberatende) der Rechnung.
        kosten (float): Die Gesamtkosten, die in der Rechnung verrechnet werden.
        db (AsyncSession): Die Datenbanksitzung für die Ausführung von asynchronen Datenbankoperationen.

    Returns:
        models.Rechnungen: Das neu erstellte Rechnungsobjekt, nachdem es der Datenbank hinzugefügt wurde.

    Raises:
        SQLAlchemyError: Wenn beim Erstellen der Rechnung ein Datenbankfehler auftritt.
    """
    rechnungsdaten = {
        "empfaenger_id": empfaenger_id,
        "steller_id": steller_id,
        "rechnungsbetrag": kosten,
        "rechnungsdatum": date.today(),
        "faelligkeitsdatum": date.today() + timedelta(days=30),
        "rechnungsart": models.Rechnungsart.Energieberater_Rechnung,
        "zahlungsstatus": models.Zahlungsstatus.Offen
    }
    neue_rechnung = models.Rechnungen(**rechnungsdaten)
    db.add(neue_rechnung)
    await db.commit()
    await db.refresh(neue_rechnung)
    return neue_rechnung


async def create_rechnung(empfaenger_id: int, steller_id: int, db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt eine Rechnung für den angegebenen Empfänger basierend auf den neuesten Energieeffizienzmaßnahmen.

    Args:
        empfaenger_id (int): Die ID des Empfängers (Haushalt), für den die Rechnung erstellt werden soll.
        steller_id (int): Die ID des Rechnungsausstellers (Energieberatende).
        db (AsyncSession): Die Datenbanksitzung für die Ausführung von asynchronen Datenbankoperationen.

    Returns:
        models.Rechnungen: Das neu erstellte Rechnungsobjekt.

    Raises:
        SQLAlchemyError: Wenn während des Vorgangs ein Datenbankfehler auftritt.
    """
    try:
        massnahme = await get_latest_massnahmen_for_haushalt(empfaenger_id, db)
        if massnahme is None:
            log_and_raise_http_exception(
                user_id=steller_id,
                endpoint="/rechnung-erstellen",
                method="POST",
                message=f"Keine Energieeffizienzmaßnahme für Haushalts-ID {empfaenger_id} gefunden",
                success=False,
                status_code=404,
                detail="Energieeffizienzmaßnahme nicht gefunden"
            )

        neue_rechnung = await create_new_rechnung(empfaenger_id, steller_id, massnahme.kosten, db)
        log_and_raise_http_exception(
            user_id=steller_id,
            endpoint="/rechnung-erstellen",
            method="POST",
            message=f"Rechnung erfolgreich erstellt für Haushalts-ID {empfaenger_id}",
            success=True,
            status_code=200,
            detail=""
        )
        return neue_rechnung

    except SQLAlchemyError as e:
        log_and_raise_http_exception(
            user_id=steller_id,
            endpoint="/rechnung-erstellen",
            method="POST",
            message=f"Datenbankfehler in create_rechnung: {e}",
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Datenbank-Fehler: {e}"
        )


async def get_energieausweis_by_id(energieausweis_id: int, db: AsyncSession):
    """
    Ruft einen Energieausweis anhand seiner ID aus der Datenbank ab.

    Args:
        energieausweis_id (int): Der eindeutige Bezeichner für den Energieausweis.
        db (AsyncSession): Die Datenbanksitzung für die Ausführung von asynchronen Datenbankoperationen.

    Returns:
        models.Energieausweise: Das abgerufene Energieausweisobjekt.

    Gibt aus:
        NoResultFound: Wenn kein Energieausweis mit der angegebenen ID existiert.
    """
    energieausweis_result = await db.execute(select(models.Energieausweise)
                                             .where(models.Energieausweise.energieausweis_id == energieausweis_id))
    return energieausweis_result.scalars().first()


async def update_or_create_haushalte_and_energieausweis(energieausweis, current_user, db: AsyncSession):
    """
    Aktualisiert den Energieausweis mit der energieberater_id und aktualisiert oder erstellt einen Haushalte-Datensatz.

    Args:
        energieausweis (models.Energieausweise): Das zu aktualisierende Energieausweisobjekt.
        current_user (models.Nutzer): Der aktuelle Benutzer, der den Vorgang durchführt.
        db (AsyncSession): Die Datenbanksitzung für die Ausführung asynchroner Datenbankoperationen.

    Returns:
        models.Haushalte: Der aktualisierte oder neu erstellte Haushalte-Datensatz.

    Raises:
        SQLAlchemyError: Wenn während des Vorgangs ein Datenbankfehler auftritt.
    """
    energieausweis.energieberater_id = current_user.user_id
    db.add(energieausweis)

    haushalte_result = await db.execute(
        select(models.Haushalte).where(models.Haushalte.user_id == energieausweis.haushalt_id))
    haushalte = haushalte_result.scalars().first()

    if haushalte:
        haushalte.energieberater_id = current_user.user_id
        haushalte.anfragestatus = True
    else:
        haushalte = models.Haushalte(
            user_id=energieausweis.haushalt_id,
            energieberater_id=current_user.user_id,
            anfragestatus=False
        )
        db.add(haushalte)

    await db.commit()
    return haushalte


@router.post("/datenanfrage/{energieausweis_id}", status_code=status.HTTP_201_CREATED)
async def datenanfrage_stellen(energieausweis_id: int = Path(..., description="Die ID des Energieausweises", gt=0),
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    """
    Stellt eine Datenanfrage für einen bestimmten Energieausweis.

    Args:
        energieausweis_id (int): Die ID des Energieausweises, für den Daten angefordert werden.
        current_user (models.Nutzer): Der aktuelle Benutzer, injizierte Abhängigkeit von OAuth.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        schemas.DatenanfrageResponse: Eine Antwort, die das Ergebnis der Datenanfrage angibt.

    Raises:
        HTTPException: Wenn das Energiezertifikat nicht gefunden werden kann oder wenn ein Datenbankfehler vorliegt.
    """
    if energieausweis_id <= 0:
        log_and_raise_http_exception(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{energieausweis_id}",
            method="POST",
            message="Ungültige Energieausweis-ID",
            success=False,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ungültige Energieausweis-ID"
        )

    try:
        energieausweis = await get_energieausweis_by_id(energieausweis_id, db)
        if not energieausweis:
            log_and_raise_http_exception(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{energieausweis_id}",
                method="POST",
                message="Energieausweis nicht gefunden",
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Energieausweis nicht gefunden"
            )

        haushalte = await update_or_create_haushalte_and_energieausweis(energieausweis, current_user, db)
        message = "Haushaltsdaten aktualisiert mit Energieberater-ID" if haushalte.anfragestatus else \
                  "Neue Haushaltsdaten erstellt und Energieberater-ID hinzugefügt"

        return schemas.DatenanfrageResponse(
            message=message,
            haushalt_id=energieausweis.haushalt_id,
            anfragestatus=haushalte.anfragestatus if haushalte else False
        )

    except SQLAlchemyError as e:
        log_and_raise_http_exception(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{energieausweis_id}",
            method="POST",
            message=f"Fehler beim Erstellen der Haushaltsdatenanfrage: {e}",
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Erstellen der Haushaltsdatenanfrage: {e}"
        )


async def validate_and_fetch_data(energieausweis_id: int, current_user, db: AsyncSession):
    """
    Überprüft das Vorhandensein eines Energieausweises und holt die zugehörigen Daten.

    Args:
        energieausweis_id (int): Die ID des Energieausweises.
        current_user (models.Nutzer): Der aktuelle Benutzer.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        Tupel: Der Energieausweis und die zugehörigen Daten.

    Raises:
        ValueError: Wenn der Energieausweis nicht gefunden werden kann.
    """
    energieausweis = await db.get(models.Energieausweise, energieausweis_id)
    if not energieausweis:
        raise ValueError("Energieausweis nicht gefunden.")

    haus_data = await db.get(models.Haushalte, energieausweis.haushalt_id)
    if not haus_data or any(attribute is None for attribute in vars(haus_data).values()):
        raise ValueError("Unvollständige Haushaltsdaten.")

    return energieausweis, haus_data


async def create_energieeffizienzmassnahme(energieausweis, massnahmen_data, db: AsyncSession):
    """
    Erzeugt eine neue Energieeffizienzmaßnahme auf der Grundlage der angegebenen Daten.

    Args:
        energieausweis (models.Energieausweise): Der zugehörige Energieausweis.
        massnahmen_data (schemas.EnergieeffizienzmassnahmenCreate): Die Daten für die neue Maßnahme.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        models.Energieeffizienzmassnahmen: Die neu erstellte Energieeffizienzmassnahme.

    Raises:
        SQLAlchemyError: Wenn während des Erstellungsprozesses ein Datenbankfehler auftrat.
    """
    neue_massnahme = models.Energieeffizienzmassnahmen(
        haushalt_id=energieausweis.haushalt_id,
        massnahmetyp=massnahmen_data.massnahmetyp,
        einsparpotenzial=massnahmen_data.einsparpotenzial,
        kosten=massnahmen_data.kosten
    )
    db.add(neue_massnahme)
    await db.commit()
    await db.refresh(neue_massnahme)
    return neue_massnahme


@router.post("/zusatzdaten-eingeben/{energieausweis_id}", status_code=status.HTTP_200_OK)
async def zusatzdaten_eingeben(energieausweis_id: int,
                               massnahmen_data: schemas.EnergieeffizienzmassnahmenCreate,
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    """
    Gibt zusätzliche Daten für einen Energieausweis und zugehörige Energieeffizienzmaßnahmen ein.

    Args:
        energieausweis_id (int): Die ID des Energieausweises.
        massnahmen_data (schemas.EnergieeffizienzmassnahmenCreate): Daten für die neuen Energieeffizienzmaßnahmen.
        current_user (models.Nutzer): Der aktuelle Nutzer, injizierte Abhängigkeit von OAuth.
        db (AsyncSession): Die Datenbanksitzung.

    Returns:
        dict: Eine Nachricht, die die erfolgreiche Eingabe von zusätzlichen Daten anzeigt.

    Raises:
        HTTPException: Wenn der Energieausweis nicht gefunden werden kann oder wenn ein Datenbankfehler vorliegt.
    """
    await check_energieberatende_role(current_user, "POST", "/daten-erfassung/{energieausweis_id}")

    try:
        energieausweis, haus_data = await validate_and_fetch_data(energieausweis_id, current_user, db)
        neue_massnahme = await create_energieeffizienzmassnahme(energieausweis, massnahmen_data, db)

        energieausweis.massnahmen_id = neue_massnahme.massnahmen_id
        await db.commit()

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/daten-erfassung/{energieausweis_id}",
            method="POST",
            message=f"Die Daten für energieausweis_id wurden erfolgreich erfasst: {energieausweis_id}",
            success=True
        )
        logger.info(logging_obj.dict())

        return {
            "message": f"Daten für Energieausweis {energieausweis_id} und zugehörige Massnahmen erfolgreich erfasst."}

    except ValueError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/daten-erfassung/{energieausweis_id}",
            method="POST",
            message=str(e),
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/daten-erfassung/{energieausweis_id}",
            method="POST",
            message=f"Datenbankfehler aufgetreten: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/daten-erfassung/{energieausweis_id}",
            method="POST",
            message=f"Unerwarteter Fehler: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unerwarteter Fehler aufgetreten") from e


@router.post("/energieausweis-erstellen/{energieausweis_id}", status_code=status.HTTP_200_OK,
             response_model=schemas.EnergieausweisCreateResponse)
async def energieausweis_erstellen(energieausweis_id: int, erstellen_data: schemas.EnergieausweisCreate,
                                   current_user: models.Nutzer = Depends(oauth.get_current_user),
                                   db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt einen Energieausweis und setzt den AusweisStatus auf 'Ausgestellt'.
    Dieser Endpunkt ermöglicht es Energieberatenden, einen Energieausweis final zu erstellen,
    indem das Ausstellungsdatum und die Gültigkeit festgelegt werden und der Status auf 'Ausgestellt' gesetzt wird.
    Voraussetzung ist, dass der AusweisStatus vorher 'AusweisAngefordert' war.
    Parameters:
    - energieausweis_id (int): Die ID des betreffenden Energieausweises.
    - erstellen_data (EnergieausweisErstellen): Ein Objekt mit den Feldern `ausstellungsdatum` und `gueltigkeit`.
    Responses:
    - 200 OK: Energieausweis erfolgreich erstellt und Status aktualisiert.
    - 400 Bad Request: Ungültige Anfrage, z.B. wenn der AusweisStatus nicht 'ZusatzdatenEingegeben' ist oder die Daten ungültig sind.
    - 404 Not Found: Energieausweis mit der angegebenen ID nicht gefunden.
    - 500 Internal Server Error: Unerwarteter Fehler, z.B. bei Datenbankproblemen.
    """
    await check_energieberatende_role(current_user, "POST", f"/energieausweis-erstellen/{energieausweis_id}")

    try:
        energieausweis = await db.get(models.Energieausweise, energieausweis_id)
        if not energieausweis:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
                method="POST",
                message=f"Energieausweis nicht gefunden für: {energieausweis_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Energieausweis nicht gefunden.")

        result = await db.execute(select(models.PVAnlage).where(models.PVAnlage.energieausweis_id == energieausweis_id))
        anlagen = result.scalars().all()

        if not anlagen:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zugehörige PVAnlagen nicht gefunden.")

        condition_met = energieausweis.ausweis_status == models.AusweisStatus.AnfrageGestellt or \
                        any(anlage.prozess_status == models.ProzessStatus.AusweisAngefordert for anlage in anlagen)

        if not condition_met:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
                method="POST",
                message=f"Ausweis Status ist nicht 'AusweisAngefordert'. für id: {energieausweis_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail="AusweisStatus ist nicht 'AnfrageGestellt' oder kein zugehöriger "
                                       "PVAnlage-Prozessstatus ist 'AusweisAngefordert'.")

        gueltigkeit = timedelta(days=int(erstellen_data.gueltigkeit_monate * 30.5)) + date.today()
        energieausweis.ausstellungsdatum = date.today()
        energieausweis.gueltigkeit = gueltigkeit
        energieausweis.energieberater_id = current_user.user_id
        energieausweis.ausweis_status = models.AusweisStatus.Ausgestellt
        energieausweis.energieeffizienzklasse = erstellen_data.energieeffizienzklasse
        energieausweis.verbrauchskennwerte = erstellen_data.verbrauchskennwerte
        await db.commit()
        await db.refresh(energieausweis)

        for anlage in anlagen:
            if anlage.prozess_status == models.ProzessStatus.AusweisAngefordert:
                anlage.prozess_status = models.ProzessStatus.AusweisErstellt
                db.add(anlage)

        await db.commit()

        await create_rechnung(empfaenger_id=energieausweis.haushalt_id, steller_id=current_user.user_id, db=db)

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
            method="POST",
            message=f"Energieausweis erfolgreich aktualisiert für id: {energieausweis_id}",
            success=True
        )
        logger.info(logging_obj.dict())

        return schemas.EnergieausweisCreateResponse(message="Energieausweis erfolgreich erstellt "
                                                            "und AusweisStatus aktualisiert",
                                                    ausweis_status='Ausgestellt')

    except SQLAlchemyError as e:
        await db.rollback()
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
            method="POST",
            message=f"Datenbankfehler aufgetreten: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler") from e
    except HTTPException as http_ex:
        await db.rollback()
        raise http_ex
    except Exception as e:
        await db.rollback()
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
            method="POST",
            message=f"Unerwarteter Fehler: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Unexpected error occurred: {e}") from e


@router.put("/abnahme-pvanlage/{anlage_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.PVAnlageAbnahmeResponse)
async def abnahmebestaetigung_fuer_pvanlagen(anlage_id: int,
                                             current_user: models.Nutzer = Depends(oauth.get_current_user),
                                             db: AsyncSession = Depends(database.get_db_async)):
    """
    Bestätigt die Abnahme einer PV-Anlage und aktualisiert den Prozessstatus.

    Diese Route ermöglicht es autorisierten Energieberatenden, die Abnahme einer PV-Anlage zu bestätigen,
    indem der Prozessstatus der Anlage auf 'Abgenommen' gesetzt wird.

    Parameters:
    - anlage_id (int): Die ID der PV-Anlage, deren Abnahme bestätigt wird.
    - current_user (models.Nutzer): Der aktuell authentifizierte Nutzer (automatisch aus dem Token geladen).
    - db (AsyncSession): Die Datenbank-Session für asynchrone DB-Operationen.

    Returns:
    - Ein Objekt vom Typ PVAnlageResponse mit einer Nachricht und dem aktualisierten Status.

    Raises:
    - HTTPException: Verschiedene Fehlercodes und Nachrichten, abhängig von der Art des aufgetretenen Fehlers.
    """

    await check_energieberatende_role(current_user, "PUT", "/abnahme-pvanlage/{anlage_id}")

    try:
        pv_anlage = await db.get(models.PVAnlage, anlage_id)
        if not pv_anlage:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/abnahme-pvanlage/{anlage_id}",
                method="PUT",
                message=f"PV-Anlage mit id {anlage_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PV-Anlage nicht gefunden")
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/abnahme-pvanlage/{anlage_id}",
            method="PUT",
            message=f"Datenbankfehler beim Abrufen der PV-Anlage: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="PV-Anlage konnte nicht abgerufen werden")

    empty_fields = [field for field, value in vars(pv_anlage).items() if value is None]
    if empty_fields:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/abnahme-pvanlage/{anlage_id}",
            method="PUT",
            message=f"PV-Anlage {anlage_id} hat fehlende Attribute: {empty_fields}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail=f"Nicht alle erforderlichen Attribute der PV-Anlage sind ausgefüllt: {empty_fields}")

    try:
        pv_anlage.prozess_status = models.ProzessStatus.Abgenommen
        db.add(pv_anlage)
        await db.commit()
        await db.refresh(pv_anlage)

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/abnahme-pvanlage/{anlage_id}",
            method="PUT",
            message=f"PV-Anlage {anlage_id} Status aktualisiert auf 'Abgenommen'",
            success=True
        )
        logger.info(logging_obj.dict())

    except SQLAlchemyError as e:
        await db.rollback()
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/abnahme-pvanlage/{anlage_id}",
            method="PUT",
            message=f"Datenbankfehler beim Aktualisieren der PV-Anlage: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=500, detail=f"Aktualisierung der PV-Anlage fehlgeschlagen")

    response = schemas.PVAnlageAbnahmeResponse(
        message=f"Abnahmebestätigung für PV-Anlage {anlage_id} erfolgreich.",
        anlage_id=anlage_id,
        prozess_status=pv_anlage.prozess_status.value
    )

    return response
