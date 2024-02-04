from datetime import date, timedelta, datetime, time
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Path, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from typing import List
from app import models, schemas, database, oauth, types
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.schemas import LoggingSchema
from io import StringIO
import io
from fastapi.responses import StreamingResponse
import csv

router = APIRouter(prefix="/solarteure", tags=["Solarteure"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_solarteur_role(current_user: models.Nutzer, method: str, endpoint: str):
    """
    Überprüft, ob der aktuelle Nutzer die Rolle "Solarteure" hat, andernfalls wird eine HTTPException ausgelöst.

    Args:
        current_user (models.Nutzer): Der aktuelle Nutzer.
        method (str): Die HTTP-Anfragemethode (z.B. "GET", "POST").
        endpoint (str): Der Endpunkt der Anfrage.

    Raises:
        HTTPException: Mit Statuscode 403, wenn der Nutzer keine Rolle "Solarteure" hat.
    """
    if current_user.rolle != models.Rolle.Solarteure:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Solarteur",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Solarteure haben Zugriff auf diese Daten")


async def check_solarteur_role_and_berater_role(current_user: models.Nutzer, method: str, endpoint: str):
    """
    Überprüft, ob der aktuelle Nutzer die Rolle "Solarteure" oder "Energieberatende" hat, andernfalls wird eine HTTPException ausgelöst.

    Args:
        current_user (models.Nutzer): Der aktuelle Nutzer.
        method (str): Die HTTP-Anfragemethode (z.B. "GET", "POST").
        endpoint (str): Der Endpunkt der Anfrage.

    Raises:
        HTTPException: Mit Statuscode 403, wenn der Nutzer keine Rolle "Solarteure" oder "Energieberatende" hat.
    """
    if current_user.rolle != models.Rolle.Solarteure and current_user.rolle != models.Rolle.Energieberatende:
        logging_error = LoggingSchema(
            user_id=current_user.user_id,
            endpoint=endpoint,
            method=method,
            message="Zugriff verweigert: Nutzer ist kein Solarteur oder Energieberater",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=403, detail="Nur Solarteure und Energieberater haben Zugriff auf diese Daten")


@router.get("/anfragen", response_model=List[schemas.PVSolarteuerResponse])
async def get_anfragen(
        prozess_status: List[types.ProzessStatus] = Query(types.ProzessStatus.AnfrageGestellt, alias="prozess_status"),
        current_user: models.Nutzer = Depends(oauth.get_current_user),
        db: AsyncSession = Depends(database.get_db_async)
):
    """
    Ruft Anfragen für Solarteure ab und gibt sie als Liste von PVSolarteuerResponse-Objekten zurück.

    Args:
        prozess_status (List[types.ProzessStatus], optional): Eine Liste von Prozessstatuswerten. Standardmäßig "AnfrageGestellt".
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        List[schemas.PVSolarteuerResponse]: Eine Liste von PVSolarteuerResponse-Objekten.

    Raises:
        HTTPException: Mit Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_solarteur_role(current_user, "GET", "/angebote")
    try:
        if (prozess_status[0] == types.ProzessStatus.AnfrageGestellt and
            (prozess_status[1] == types.ProzessStatus.DatenAngefordert) and
                (prozess_status[2] == types.ProzessStatus.DatenFreigegeben)):
            query = (select(models.PVAnlage, models.Nutzer, models.Adresse)
                     .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                     .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                     .where(models.PVAnlage.prozess_status.in_([models.ProzessStatus.AnfrageGestellt,
                                                                models.ProzessStatus.DatenFreigegeben,
                                                                models.ProzessStatus.DatenAngefordert,
                                                                models.ProzessStatus.AngebotAbgelehnt]
                             )))

        else:
            query = (select(models.PVAnlage, models.Nutzer, models.Adresse)
                     .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                     .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id))

            print(prozess_status)
            if prozess_status:
                query = query.where((models.PVAnlage.prozess_status.in_(prozess_status))
                                    & (models.PVAnlage.solarteur_id == current_user.user_id))
        result = await db.execute(query)
        anfragen = result.all()

        if not anfragen:
            return []

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
        } for angebot, nutzer, adresse in anfragen]

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebote",
            method="GET",
            message=f"Fehler beim Abrufen der Angebote: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Abrufen der Angebote: {e}")


@router.get("/anfragen/{anlage_id}", response_model=schemas.PVSolarteuerResponse)
async def get_anfrage(anlage_id: int, current_user: models.Nutzer = Depends(oauth.get_current_user),
                      db: AsyncSession = Depends(database.get_db_async)):
    """
    Ruft eine bestimmte Anfrage für einen Solarteur ab und gibt sie als PVSolarteuerResponse-Objekt zurück.

    Args:
        anlage_id (int): Die ID der PV-Anlage.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        schemas.PVSolarteuerResponse: Ein PVSolarteuerResponse-Objekt.

    Raises:
        HTTPException: Mit Statuscode 404, wenn die Anfrage nicht gefunden wurde, oder Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_solarteur_role_and_berater_role(current_user, "GET", f"/angebote/{anlage_id}")

    try:
        stmt = (select(models.PVAnlage, models.Nutzer, models.Adresse)
                .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                .where(models.PVAnlage.anlage_id == anlage_id))

        result = await db.execute(stmt)
        angebot = result.first()

        if not angebot:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/angebote/{anlage_id}",
                method="GET",
                message="Angebot nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Anfrage {anlage_id} nicht gefunden")

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
            "stadt": angebot[2].stadt
        }

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebote/{anlage_id}",
            method="GET",
            message=f"Fehler beim Abrufen des Angebots: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Fehler beim Abrufen des Angebots: {e}")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/angebote/{anlage_id}",
            method="GET",
            message=f"Fehler beim Abrufen des Angebots: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Abrufen des Angebots: {e}")


#  TODO:  Check funktion hier
@router.post("/angebote", status_code=status.HTTP_201_CREATED, response_model=schemas.AngebotResponse)
async def create_angebot(angebot_data: schemas.AngebotCreate,
                         current_user: models.Nutzer = Depends(oauth.get_current_user),
                         db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt ein Angebot für eine PV-Anlage und gibt es als AngebotResponse-Objekt zurück.

    Args:
        angebot_data (schemas.AngebotCreate): Die Daten für das Angebot.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        schemas.AngebotResponse: Ein AngebotResponse-Objekt mit den erstellten Angebotsinformationen.

    Raises:
        HTTPException: Mit Statuscode 404, wenn die PV-Anlage nicht gefunden wurde, oder Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_solarteur_role(current_user, "POST", "/angebote")

    pv_anlage = await db.get(models.PVAnlage, angebot_data.anlage_id)
    if not pv_anlage:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebote",
            method="POST",
            message="PV-Anlage nicht gefunden",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PV-Anlage nicht gefunden "
        )

    if pv_anlage.prozess_status != models.ProzessStatus.AnfrageGestellt and pv_anlage.prozess_status \
            != models.ProzessStatus.DatenFreigegeben:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebote",
            method="POST",
            message="Nicht berechtigt, ein Angebot für diese PV-Anlage zu erstellen.",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Nicht berechtigt, ein Angebot für diese PV-Anlage zu erstellen.")

    haushalt = await db.execute(select(models.Haushalte).where(models.Haushalte.user_id == pv_anlage.haushalt_id))
    haushalt = haushalt.scalars().first()
    if not haushalt or any([
        haushalt.anzahl_bewohner is None,
        haushalt.heizungsart is None,
        haushalt.baujahr is None,
        haushalt.wohnflaeche is None,
        haushalt.isolierungsqualitaet is None,
        haushalt.ausrichtung_dach is None,
        haushalt.dachflaeche is None,
        haushalt.energieeffizienzklasse is None
    ]):
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebote",
            method="POST",
            message="Vollständiger Haushaltsdatensatz für den angegebenen Haushalt nicht vorhanden.",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Vollständiger Haushaltsdatensatz für den angegebenen Haushalt nicht vorhanden."
        )

    dashboard_daten_existieren = await db.execute(
        select(models.DashboardSmartMeterData).where(models.DashboardSmartMeterData.haushalt_id == haushalt.user_id))
    if not dashboard_daten_existieren.scalars().first():
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/angebote",
            method="POST",
            message="Keine Dashboard-Daten für den angegebenen Haushalt vorhanden.",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Keine Dashboard-Daten für den angegebenen Haushalt vorhanden."
        )

    neues_angebot = models.Angebot(
        anlage_id=angebot_data.anlage_id,
        kosten=angebot_data.kosten
    )
    db.add(neues_angebot)
    await db.commit()
    await db.refresh(neues_angebot)

    pv_anlage.modultyp = angebot_data.modultyp
    pv_anlage.kapazitaet = angebot_data.kapazitaet
    pv_anlage.installationsflaeche = angebot_data.installationsflaeche
    pv_anlage.prozess_status = models.ProzessStatus.AngebotGemacht
    pv_anlage.modulanordnung = angebot_data.modulanordnung
    pv_anlage.solarteur_id = current_user.user_id
    await db.commit()

    logging_obj = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/angebote",
        method="POST",
        message="Angebot erfolgreich erstellt!",
        success=False
    )
    logger.info(logging_obj.dict())

    return schemas.AngebotResponse(
        angebot_id=neues_angebot.angebot_id,
        anlage_id=neues_angebot.anlage_id,
        kosten=neues_angebot.kosten
    )


async def add_calendar_entry(db: AsyncSession, user_id: int, start: datetime, ende: datetime, beschreibung: str,
                             allDay: bool = False):
    new_entry = models.Kalendereintrag(
        user_id=user_id,
        start=start,
        ende=ende,
        beschreibung=beschreibung,
        allDay=allDay
    )
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry


@router.post("/installationsplan/{anlage_id}", status_code=status.HTTP_201_CREATED,
             response_model=schemas.InstallationsplanResponse)
async def create_installationsplan(anlage_id: int, installationsplan_data: schemas.InstallationsplanCreate,
                                   current_user: models.Nutzer = Depends(oauth.get_current_user),
                                   db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt einen Installationsplan für eine PV-Anlage und gibt ihn als InstallationsplanResponse-Objekt zurück.

    Args:
        anlage_id (int): Die ID der PV-Anlage.
        installationsplan_data (schemas.InstallationsplanCreate): Die Daten für den Installationsplan.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        schemas.InstallationsplanResponse: Ein InstallationsplanResponse-Objekt mit den erstellten Installationsplaninformationen.

    Raises:
        HTTPException: Mit Statuscode 404, wenn die PV-Anlage nicht gefunden wurde, oder Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    await check_solarteur_role(current_user, "POST", f"/pv_anlagen/installationsplan/{anlage_id}")

    pv_anlage = await db.get(models.PVAnlage, anlage_id)
    if not pv_anlage or pv_anlage.solarteur_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PV-Anlage nicht gefunden oder gehört nicht zum aktuellen Solarteur."
        )

    pv_anlage.kabelwegfuehrung = installationsplan_data.kabelwegfuehrung
    pv_anlage.montagesystem = installationsplan_data.montagesystem
    pv_anlage.schattenanalyse = installationsplan_data.schattenanalyse
    pv_anlage.wechselrichterposition = installationsplan_data.wechselrichterposition
    pv_anlage.installationsdatum = installationsplan_data.installationsdatum
    pv_anlage.prozess_status = "PlanErstellt"

    installationsdatum = datetime.combine(installationsplan_data.installationsdatum, time(8, 0))  # 8 Uhr Start
    ende_datum = installationsdatum + timedelta(hours=4)  # Annahme: 4-Stunden-Installation
    beschreibung = f"Installation einer PV-Anlage: {anlage_id}"

    await add_calendar_entry(db, current_user.user_id, installationsdatum, ende_datum, beschreibung)

    installationsplan_csv = StringIO()
    writer = csv.writer(installationsplan_csv)
    writer.writerow(
        ['Kabelwegführung', 'Montagesystem', 'Schattenanalyse', 'Wechselrichterposition', 'Installationsdatum'])
    writer.writerow([
        installationsplan_data.kabelwegfuehrung,
        installationsplan_data.montagesystem,
        installationsplan_data.schattenanalyse,
        installationsplan_data.wechselrichterposition,
        installationsplan_data.installationsdatum.strftime("%Y-%m-%d")
    ])

    installationsplan_path = f"app/data/installationsplan_{anlage_id}.csv"
    pv_anlage.installationsplan = installationsplan_path

    with open(installationsplan_path, 'w') as f:
        f.write(installationsplan_csv.getvalue())

    await db.commit()

    await create_rechnung(anlage_id=anlage_id, steller_id=current_user.user_id, db=db)

    return schemas.InstallationsplanResponse(installationsplan=pv_anlage.installationsplan)

@router.get("/installationsplan/{anlage_id}")
async def get_installationsplan(anlage_id: int,
                                db: AsyncSession = Depends(database.get_db_async),
                                current_user: models.Nutzer = Depends(oauth.get_current_user)):
    """
    Ruft den Installationsplan für eine PV-Anlage ab und gibt ihn als CSV-Datei zurück.

    Args:
        anlage_id (int): Die ID der PV-Anlage.
        current_user (models.Nutzer, optional): Der aktuelle Nutzer. Standardmäßig None.
        db (AsyncSession, optional): Die Datenbankverbindung. Standardmäßig None.

    Returns:
        CSV-Datei: Der Installationsplan als CSV-Datei.

    Raises:
        HTTPException: Mit Statuscode 404, wenn die PV-Anlage nicht gefunden wurde, oder Statuscode 500 für eventuelle serverseitige Fehler während des Prozesses.
    """
    try:
        pv_anlage = await db.get(models.PVAnlage, anlage_id)
        if not pv_anlage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PV-Anlage nicht gefunden oder gehört nicht zum aktuellen Solarteur."
            )

        installationsplan = pv_anlage.installationsplan
        if not installationsplan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installationsplan nicht gefunden."
            )

        with open(installationsplan, 'rb') as f:
            plan_csv = f.read()

        return StreamingResponse(io.BytesIO(plan_csv), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={installationsplan}"})

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/installationsplan/",
            method="GET",
            message=f"Fehler beim Abrufen des Installationsplans: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen des Installationsplans: {e}"
        )


async def create_rechnung(anlage_id: int, steller_id: int, db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt eine Rechnung für eine PV-Anlage.

    Parameter:
    - anlage_id (int): Die ID der PV-Anlage.
    - steller_id (int): Die ID des Rechnungsausstellers (Solarteur).
    - db (AsyncSession): Die Datenbank-Session-Abhängigkeit.

    Returns:
    - Rechnungen: Das erstellte Rechnungsobjekt.

    Raises:
    - HTTPException: Wenn die PV-Anlage oder das entsprechende Angebot nicht gefunden wird,
                     oder im Falle eines Datenbankfehlers.
    """
    try:
        pv_anlage_result = await db.execute(select(models.PVAnlage).where(models.PVAnlage.anlage_id == anlage_id))
        pv_anlage = pv_anlage_result.scalar_one_or_none()

        if not pv_anlage:
            logging_obj = schemas.LoggingSchema(
                user_id=steller_id,
                endpoint=f"/installationsplan/",
                method="POST",
                message=f"PV-Anlage mit ID {anlage_id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="PV-Anlage nicht gefunden")

        empfaenger_id = pv_anlage.haushalt_id

        angebot_result = await db.execute(
            select(models.Angebot)
            .join(models.PVAnlage, models.Angebot.anlage_id == models.PVAnlage.anlage_id)
            .where(models.PVAnlage.anlage_id == anlage_id,
                   models.PVAnlage.prozess_status == models.ProzessStatus.PlanErstellt)
            .order_by(models.Angebot.created_at.desc())
        )
        angebot = angebot_result.scalar_one_or_none()

        if not angebot:
            logging_obj = schemas.LoggingSchema(
                user_id=steller_id,
                endpoint=f"/installationsplan/",
                method="POST",
                message=f"Kein akzeptiertes Angebot für PV-Anlagen-ID {anlage_id} gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Angebot nicht gefunden oder nicht angenommen")

        rechnungsdaten = {
            "empfaenger_id": empfaenger_id,
            "steller_id": steller_id,
            "rechnungsbetrag": angebot.kosten,
            "rechnungsdatum": date.today(),
            "faelligkeitsdatum": date.today() + timedelta(days=30),
            "rechnungsart": models.Rechnungsart.Solarteur_Rechnung,
            "zahlungsstatus": models.Zahlungsstatus.Offen
        }
        neue_rechnung = models.Rechnungen(**rechnungsdaten)
        db.add(neue_rechnung)
        await db.commit()
        await db.refresh(neue_rechnung)

        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/installationsplan/",
            method="POST",
            message=f"Rechnung erfolgreich erstellt für PV-Anlage-ID {anlage_id}",
            success=True
        )
        logger.error(logging_obj.dict())

        return neue_rechnung

    except NoResultFound:
        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/installationsplan/",
            method="POST",
            message=f"Kein Ergebnis bei der Abfrage des Angebots für die PV-Anlagen-ID {anlage_id} gefunden",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Keine Daten zum Angebot gefunden")

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/installationsplan/",
            method="POST",
            message=f"Datenbankfehler in create_rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Datenbank-Fehler: {e}")
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/installationsplan/",
            method="POST",
            message=f"Unerwarteter Fehler in create_rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unerwarteter Fehler: {e}")


@router.get("/offene_pv_anlagen", status_code=status.HTTP_200_OK, response_model=list[schemas.PVAnlageResponse])
async def offene_pv_anlagen_abrufen(current_user: models.Nutzer = Depends(oauth.get_current_user),
                                    db: AsyncSession = Depends(database.get_db_async)):
    """
    Ruft offene PV-Anlagen ab, die noch keinem Solarteur zugewiesen sind.

    Args:
        current_user (models.Nutzer): Der aktuelle Nutzer.
        db (AsyncSession): Die Datenbankverbindung.

    Returns:
        List[schemas.PVAnlageResponse]: Eine Liste von PV-Anlage-Objekten.

    Raises:
        HTTPException: Mit Statuscode 500, wenn ein Fehler beim Abrufen der PV-Anlagen auftritt.
    """
    await check_solarteur_role(current_user, "GET", "/offene_pv_anlagen")

    try:
        result = await db.execute(select(models.PVAnlage).where(models.PVAnlage.solarteur_id == None))
        offene_anlagen = result.scalars().all()

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/offene_pv_anlagen",
            method="GET",
            message="PV-Anlagen erfolgreich abgerugen",
            success=False
        )
        logger.info(logging_obj.dict())

        return offene_anlagen
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/offene_pv_anlagen",
            method="GET",
            message=f"Fehler beim Abrufen offener PV-Anlagen: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Abrufen offener PV-Anlagen: {e}")


@router.post("/datenanfrage/{anlage_id}", status_code=status.HTTP_201_CREATED)
async def datenanfrage_stellen(anlage_id: int = Path(..., description="Die ID der PV-Anlage", gt=0),
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    """
    Stellt eine Datenanfrage für eine bestimmte PV-Anlage und aktualisiert den Anfragestatus.

    Args:
        anlage_id (int): Die ID der PV-Anlage.
        current_user (models.Nutzer): Der aktuelle Nutzer.
        db (AsyncSession): Die Datenbankverbindung.

    Returns:
        schemas.DatenanfrageResponse: Eine Antwort mit Informationen zur Datenanfrage.

    Raises:
        HTTPException: Mit Statuscode 404, wenn die PV-Anlage nicht gefunden wird.
                      Mit Statuscode 422, wenn die Anlage-ID ungültig ist.
                      Mit Statuscode 500, wenn ein anderer Fehler auftritt.
    """
    await check_solarteur_role(current_user, "POST", f"/datenanfrage/{anlage_id}")

    if anlage_id <= 0:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{anlage_id}",
            method="POST",
            message="Ungültige Anlage-ID",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ungültige Anlage-ID")

    try:
        pv_anlage_result = await db.execute(select(models.PVAnlage).where(models.PVAnlage.anlage_id == anlage_id))
        pv_anlage = pv_anlage_result.scalars().first()
        if not pv_anlage:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{anlage_id}",
                method="POST",
                message="PV-Anlage nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PV-Anlage nicht gefunden")
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{anlage_id}",
            method="POST",
            message=f"Fehler beim Abrufen der PV-Anlage: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Abrufen der PV-Anlage: {e}")

    try:
        haushaltsdaten_existieren = await db.execute(
            select(models.Haushalte).where(models.Haushalte.user_id == pv_anlage.haushalt_id))
        haushaltsdaten_existieren = haushaltsdaten_existieren.scalars().first()
        if haushaltsdaten_existieren is not None:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{anlage_id}",
                method="POST",
                message="Haushaltsdaten existieren bereits",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Haushaltsdaten existieren bereits oder Anfrage wurde bereits gestellt")
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{anlage_id}",
            method="POST",
            message=f"Fehler beim Überprüfen der Haushaltsdaten: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Überprüfen der Haushaltsdaten: {e}")

    try:
        neue_haushaltsdaten = models.Haushalte(
            user_id=pv_anlage.haushalt_id,
            anfragestatus=False  # False, da die Anfrage noch nicht bestätigt wurde
        )
        db.add(neue_haushaltsdaten)
        pv_anlage.prozess_status = models.ProzessStatus.DatenAngefordert
        await db.commit()
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{anlage_id}",
            method="POST",
            message=f"Fehler beim Erstellen der Haushaltsdatenanfrage: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Erstellen der Haushaltsdatenanfrage: {e}")

    logging_obj = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint=f"/datenanfrage/{anlage_id}",
        method="POST",
        message=f"Datenanfrage erfolgreich gestellt",
        success=True
    )
    logger.info(logging_obj.dict())

    return schemas.DatenanfrageResponse(
        message="Datenanfrage erfolgreich gestellt",
        haushalt_id=pv_anlage.haushalt_id,
        anfragestatus=neue_haushaltsdaten.anfragestatus)
