from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
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


@router.post("/rechnungen", response_model=schemas.RechnungResponse, status_code=status.HTTP_201_CREATED)
async def create_rechnung(rechnung: schemas.RechnungCreate, db: AsyncSession = Depends(database.get_db_async)):
    try:
        # Hier holen wir die Energieeffizienzmaßnahmen des Nutzers, um die Kosten zu erhalten.
        massnahmen_query = select(models.Energieeffizienzmassnahmen).where(
            models.Energieeffizienzmassnahmen.haushalt_id == rechnung.user_id
        )
        massnahmen_result = await db.execute(massnahmen_query)
        massnahme = massnahmen_result.scalar_one_or_none()

        if massnahme is None:
            raise HTTPException(status_code=404, detail="Energieeffizienzmaßnahme nicht gefunden")

        # Setzen der Kosten als Rechnungsbetrag
        rechnung_dict = rechnung.dict()
        rechnung_dict["rechnungsbetrag"] = massnahme.kosten

        neue_rechnung = models.Rechnungen(**rechnung_dict)
        db.add(neue_rechnung)
        await db.commit()
        await db.refresh(neue_rechnung)
        return neue_rechnung
    except SQLAlchemyError as e:
        logger.error(f"Rechnung konnte nicht erstellt werden: {e}")
        raise HTTPException(status_code=500, detail=f"Rechnung konnte nicht erstellt werden: {e}")


@router.post("/datenanfrage/{energieausweis_id}", status_code=status.HTTP_201_CREATED)
async def datenanfrage_stellen(energieausweis_id: int = Path(..., description="Die ID des Energieausweises", gt=0),
                               current_user: models.Nutzer = Depends(oauth.get_current_user),
                               db: AsyncSession = Depends(database.get_db_async)):
    await check_energieberatende_role(current_user, "POST", f"/datenanfrage/{energieausweis_id}")

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
        if energieausweis.energieberater_id != current_user.user_id:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{energieausweis_id}",
                method="POST",
                message="Nicht autorisiert für diesen Energieausweis",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Nicht autorisiert für diesen Energieausweis")
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{energieausweis_id}",
            method="POST",
            message=f"Fehler beim Abrufen der Energieausweise: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Abrufen der Energieausweise: {e}")

    try:
        haushaltsdaten_existieren = await db.execute(
            select(models.Haushalte).where(models.Haushalte.user_id == energieausweis.haushalt_id))
        if haushaltsdaten_existieren.scalars().first():
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{energieausweis_id}",
                method="POST",
                message="Haushaltsdaten existieren bereits oder Anfrage wurde bereits gestellt",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Haushaltsdaten existieren bereits oder Anfrage wurde bereits gestellt")
    except SQLAlchemyError as e:
        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/datenanfrage/{energieausweis_id}",
            method="POST",
            message=f"Fehler beim Überprüfen der Haushaltsdaten: {e}",
            success=False
        )
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Fehler beim Überprüfen der Haushaltsdaten: {e}")

    try:
        neue_haushaltsdaten = models.Haushalte(
            user_id=energieausweis.haushalt_id,
            anfragestatus=False  # False, da die Anfrage noch nicht bestätigt wurde
        )
        db.add(neue_haushaltsdaten)
        await db.commit()
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
        message="Datenanfrage erfolgreich gestellt",
        haushalt_id=energieausweis.haushalt_id,
        anfragestatus=neue_haushaltsdaten.anfragestatus)


@router.post("/zusatzdaten-eingeben/{energieausweis_id}", status_code=status.HTTP_200_OK)
async def zusatzdaten_eingeben(energieausweis_id: int, energieausweis_data: schemas.EnergieausweiseUpdate,
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
        user_id = energieausweis.energieberater_id
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

        if energieausweis.ausweis_status != models.AusweisStatus.AnfrageGestellt:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/daten-erfassung/{energieausweis_id}",
                method="POST",
                message=f"Ausweis status is not 'AnfrageGestellt' for id: {energieausweis_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ausweis Status ist nicht 'AnfrageGestellt'.")

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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Haushaltsdaten sind unvollständig.")

        energieausweis.energieeffizienzklasse = energieausweis_data.energieeffizienzklasse
        energieausweis.verbrauchskennwerte = energieausweis_data.verbrauchskennwerte
        energieausweis.ausweis_status = models.AusweisStatus.ZusatzdatenEingegeben

        neue_massnahme = models.Energieeffizienzmassnahmen(
            haushalt_id=energieausweis.haushalt_id,
            massnahmetyp=massnahmen_data.massnahmetyp,
            energieberater_id=user_id,
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
        if not energieausweis_id:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
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
                endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
                method="POST",
                message=f"Energieausweis nicht gefunden für: {energieausweis_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Energieausweis nicht gefunden.")

        if energieausweis.ausweis_status != models.AusweisStatus.ZusatzdatenEingegeben:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
                method="POST",
                message=f"Ausweis status is not 'ZusatzdatenEingegeben' for id: {energieausweis_id}",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ausweis Status ist nicht 'ZusatzdatenEingegeben'.")

        if erstellen_data.gueltigkeit <= erstellen_data.ausstellungsdatum:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/energieausweis-erstellen/{energieausweis_id}",
                method="POST",
                message=f"Gültigkeit muss später als das Ausstellungsdatum sein.",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Gültigkeit muss später als das Ausstellungsdatum sein.")

        energieausweis.ausstellungsdatum = erstellen_data.ausstellungsdatum
        energieausweis.gueltigkeit = erstellen_data.gueltigkeit
        energieausweis.ausweis_status = models.AusweisStatus.Ausgestellt

        await db.commit()

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
                            detail="Unexpected error occurred") from e


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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
