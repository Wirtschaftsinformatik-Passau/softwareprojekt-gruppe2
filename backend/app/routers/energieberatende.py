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


@router.get("/anfragen", response_model=List[schemas.PVSolarteuerResponse])
async def get_anfragen(
        prozess_status: List[types.ProzessStatus] = Query(None),
        current_user: models.Nutzer = Depends(oauth.get_current_user),
        db: AsyncSession = Depends(database.get_db_async)
):
    await check_energieberatende_role(current_user, "GET", "/angebote")
    try:
        if prozess_status[0] == types.ProzessStatus.AusweisAngefordert and (len(prozess_status) == 1):
            query = (select(models.PVAnlage, models.Nutzer, models.Adresse, None)
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
        result = await db.execute(query)
        anfragen = result.all()
        print(anfragen)

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
        } for angebot, nutzer, adresse, ausweis in anfragen]

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


@router.get("/anfragen/{anlage_id}")
async def get_anfrage(anlage_id: int, current_user: models.Nutzer = Depends(oauth.get_current_user),
                      db: AsyncSession = Depends(database.get_db_async)):
    await check_energieberatende_role(current_user, "GET", f"/angebote/{anlage_id}")

    try:
        stmt = (select(models.PVAnlage, models.Nutzer, models.Adresse, models.Energieausweise)
                .join(models.Nutzer, models.Nutzer.user_id == models.PVAnlage.haushalt_id)
                .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
                .join(models.Energieausweise,
                      models.PVAnlage.energieausweis_id == models.Energieausweise.energieausweis_id)
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


async def create_rechnung(empfaenger_id: int,  steller_id: int, db: AsyncSession = Depends(database.get_db_async)):
    """
    Erstellt eine Rechnung für Energieeffizienzmaßnahmen.

    Parameter:
    - empfaenger_id (int): Die ID des Rechnungsempfängers (Haushalt).
    - steller_id (int): Die ID des Rechnungsausstellers (Energieberater).
    - db (AsyncSession): Die Datenbank-Session-Abhängigkeit.

    Returns:
    - Rechnungen: Das erstellte Rechnungsobjekt.

    Raises:
    - HTTPException: Wenn keine Energieeffizienzmaßnahme gefunden wird oder wenn ein Datenbankfehler auftritt.
    """
    try:
        massnahmen_query = (select(models.Energieeffizienzmassnahmen)
                            .where(models.Energieeffizienzmassnahmen.haushalt_id == empfaenger_id)
                            .order_by(models.Energieeffizienzmassnahmen.created_at.desc())
                            .limit(1))
        massnahmen_result = await db.execute(massnahmen_query)
        massnahme = massnahmen_result.scalars().first()

        if massnahme is None:
            logging_obj = schemas.LoggingSchema(
                user_id=steller_id,
                endpoint=f"/energieausweis-erstellen/",
                method="POST",
                message=f"Keine Energieeffizienzmaßnahme für Haushalts-ID {empfaenger_id} gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=404, detail="Energieeffizienzmaßnahme nicht gefunden")

        rechnungsdaten = {
            "empfaenger_id": empfaenger_id,
            "steller_id": steller_id,
            "rechnungsbetrag": massnahme.kosten,
            "rechnungsdatum": date.today(),
            "faelligkeitsdatum": date.today() + timedelta(days=30),
            "rechnungsart": models.Rechnungsart.Energieberater_Rechnung
        }

        neue_rechnung = models.Rechnungen(**rechnungsdaten)
        db.add(neue_rechnung)
        await db.commit()
        await db.refresh(neue_rechnung)

        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/energieausweis-erstellen/",
            method="POST",
            message=f"Rechnung erfolgreich erstellt für Haushalts-ID {empfaenger_id}",
            success=True
        )
        logger.info(logging_obj.dict())

        return neue_rechnung

    except NoResultFound:
        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/energieausweis-erstellen/",
            method="POST",
            message=f"Kein Ergebnis bei der Abfrage nach Energieeffizienzmaßnahmen "
                    f"für Haushalts-ID {empfaenger_id} gefunden",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Keine Daten zur Energieeffizienzmaßnahme gefunden")

    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/energieausweis-erstellen/",
            method="POST",
            message=f"Datenbankfehler in create_rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Datenbank-Fehler: {e}")
    except Exception as e:
        logging_obj = schemas.LoggingSchema(
            user_id=steller_id,
            endpoint=f"/energieausweis-erstellen/",
            method="POST",
            message=f"Unerwarteter Fehler in create_rechnung: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unerwarteter Fehler: {e}")


@router.post("/datenanfrage/{energieausweis_id}", status_code=status.HTTP_201_CREATED)
async def datenanfrage_stellen(energieausweis_id: int = Path(..., description="Die ID des Energieausweises", gt=0),
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    if energieausweis_id <= 0:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{energieausweis_id}",
            method="POST",
            message="Ungültige Energieausweis-ID",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ungültige Energieausweis-ID")

    try:
        energieausweis_result = await db.execute(select(models.Energieausweise)
                                                 .where(models.Energieausweise.energieausweis_id == energieausweis_id))
        energieausweis = energieausweis_result.scalars().first()
        if not energieausweis:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{energieausweis_id}",
                method="POST",
                message="Energieausweis nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Energieausweis nicht gefunden")

        energieausweis.energieberater_id = current_user.user_id
        await db.commit()

        haushalte_result = await db.execute(
            select(models.Haushalte).where(models.Haushalte.user_id == energieausweis.haushalt_id))
        haushalte = haushalte_result.scalars().first()

        if haushalte:
            haushalte.energieberater_id = current_user.user_id
            haushalte.anfragestatus = True
            await db.commit()
            message = "Haushaltsdaten aktualisiert mit Energieberater-ID"
        else:
            haushalte = models.Haushalte(
                user_id=energieausweis.haushalt_id,
                energieberater_id=current_user.user_id,
                anfragestatus=False
            )
            db.add(haushalte)
            await db.commit()
            message = "Neue Haushaltsdaten erstellt und Energieberater-ID hinzugefügt"
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{energieausweis_id}",
            method="POST",
            message=f"Fehler beim Erstellen der Haushaltsdatenanfrage: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Erstellen der Haushaltsdatenanfrage: {e}")

    logging_obj = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint=f"/datenanfrage/{energieausweis_id}",
        method="POST",
        message=f"Datenanfrage erfolgreich gestellt",
        success=True
    )
    logger.info(logging_obj.dict())

    return schemas.DatenanfrageResponse(
        message=message,
        haushalt_id=energieausweis.haushalt_id,
        anfragestatus=haushalte.anfragestatus if haushalte else False)


@router.post("/zusatzdaten-eingeben/{energieausweis_id}", status_code=status.HTTP_200_OK)
async def zusatzdaten_eingeben(energieausweis_id: int,
                               massnahmen_data: schemas.EnergieeffizienzmassnahmenCreate,
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    """
    Erfasst und gibt zusätzliche Daten für einen Energieausweis und Energieeffizienzmassnahmen ein.
    Dieser Endpunkt ermöglicht es Energieberatenden, zusätzliche Daten zu einem Energieausweis hinzuzufügen
    und neue Maßnahmen für die Energieeffizienz zu erfassen.
    - `energieausweis_id`: Eindeutige ID des Energieausweises.
    - `energieausweis_data`: Aktualisierte Daten für den Energieausweis.
    - `massnahmen_data`: Daten für die zu erstellenden Energieeffizienzmassnahmen.
    ## Responses
    - '200 OK': Daten erfolgreich erfasst.
    - '400 Bad Request': Ungültige Anfrage, z.B. unvollständige Haushaltsdaten.
    - '404 Not Found': Energieausweis nicht gefunden.
    - '500 Internal Server Error': Unerwarteter Fehler.
    """
    await check_energieberatende_role(current_user, "POST", "/daten-erfassung/{energieausweis_id}")
    try:
        if not energieausweis_id:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/daten-erfassung/{energieausweis_id}",
                method="POST",
                message="Ungültige Energieausweis-ID angegeben",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungültige Energieausweis-ID angegeben")

        energieausweis = await db.get(models.Energieausweise, energieausweis_id)

        if not energieausweis:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/daten-erfassung/{energieausweis_id}",
                method="POST",
                message=f"Energieausweis nicht gefunden für: {energieausweis_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Energieausweis nicht gefunden.")

        haus_data = await db.get(models.Haushalte, energieausweis.haushalt_id)
        if not haus_data or any(attribute is None for attribute in vars(haus_data).values()):
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/daten-erfassung/{energieausweis_id}",
                method="POST",
                message=f"Unvollständige Haushaltsdaten für haushalt_id: {energieausweis.haushalt_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail="Haushaltsdaten sind unvollständig.")

        neue_massnahme = models.Energieeffizienzmassnahmen(
            haushalt_id=energieausweis.haushalt_id,
            massnahmetyp=massnahmen_data.massnahmetyp,
            einsparpotenzial=massnahmen_data.einsparpotenzial,
            kosten=massnahmen_data.kosten
        )
        db.add(neue_massnahme)
        await db.commit()
        await db.refresh(neue_massnahme)

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

    except SQLAlchemyError as e:
        await db.rollback()
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/daten-erfassung/{energieausweis_id}",
            method="POST",
            message=f"Es ist ein Datenbankfehler aufgetreten: {str(e)}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler") from e
    except HTTPException as http_ex:
        await db.rollback()
        raise http_ex
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
    Voraussetzung ist, dass der AusweisStatus vorher 'ZusatzdatenEingegeben' war.
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
