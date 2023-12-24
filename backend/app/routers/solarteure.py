from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app import models, schemas, database, oauth, types
import logging
from logging.config import dictConfig
from app.logger import LogConfig
from app.schemas import LoggingSchema
from io import StringIO
import csv

router = APIRouter(prefix="/solarteure", tags=["Solarteure"])

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


async def check_solarteur_role(current_user: models.Nutzer, method: str, endpoint: str):
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


@router.post("/angebote", status_code=status.HTTP_201_CREATED, response_model=schemas.AngebotResponse)
async def create_angebot(angebot_data: schemas.AngebotCreate,
                         current_user: models.Nutzer = Depends(oauth.get_current_user),
                         db: AsyncSession = Depends(database.get_db_async)):
    await check_solarteur_role(current_user, "POST", "/angebote")

    pv_anlage = await db.get(models.PVAnlage, angebot_data.anlage_id)
    if not pv_anlage or pv_anlage.solarteur_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PV-Anlage nicht gefunden oder gehört nicht zum aktuellen Solarteur."
        )

    if pv_anlage.prozess_status != models.ProzessStatus.AnfrageGestellt:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Nicht berechtigt, ein Angebot für diese PV-Anlage zu erstellen.")

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
    await db.commit()

    return schemas.AngebotResponse(
        angebot_id=neues_angebot.angebot_id,
        anlage_id=neues_angebot.anlage_id,
        kosten=neues_angebot.kosten
    )


@router.post("/installationsplan/{anlage_id}", status_code=status.HTTP_201_CREATED,
             response_model=schemas.InstallationsplanResponse)
async def create_installationsplan(anlage_id: int, installationsplan_data: schemas.InstallationsplanCreate,
                                   current_user: models.Nutzer = Depends(oauth.get_current_user),
                                   db: AsyncSession = Depends(database.get_db_async)):
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

    return schemas.InstallationsplanResponse(installationsplan=pv_anlage.installationsplan)


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


@router.get("/offene_pv_anlagen", status_code=status.HTTP_200_OK, response_model=list[schemas.PVAnlageResponse])
async def offene_pv_anlagen_abrufen(current_user: models.Nutzer = Depends(oauth.get_current_user),
                                    db: AsyncSession = Depends(database.get_db_async)):
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
        if pv_anlage.solarteur_id != current_user.user_id:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{anlage_id}",
                method="POST",
                message="Nicht autorisiert für diese PV-Anlage",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nicht autorisiert für diese PV-Anlage")
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
        if haushaltsdaten_existieren.scalars().first():
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/datenanfrage/{anlage_id}",
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
        pv_anlage.prozess_status = 'DatenAngefordert'
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
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

