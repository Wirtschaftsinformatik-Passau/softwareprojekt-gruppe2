from datetime import MAXYEAR, date
from datetime import date, datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
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


@router.post("/angebot-anfordern", response_model=schemas.PVAnforderungResponse)
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

        return schemas.PVAnlageResponse(
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


@router.post("/tarifantrag", response_model=schemas.VertragResponse)
async def tarifantrag_stellen(tarif_antrag: schemas.TarifAntragCreate, 
                              db: AsyncSession = Depends(database.get_db_async),
                              current_user: models.Nutzer = Depends(oauth.get_current_user)):
    await check_haushalt_role(current_user, "POST", "/tarifantrag")

    # Überprüfen, ob der angeforderte Tarif existiert
    tarif = await db.get(models.Tarif, tarif_antrag.tarif_id)
    if not tarif:
        raise HTTPException(status_code=404, detail="Tarif nicht gefunden")

    # Erstellen des Vertrags
    neuer_vertrag = models.Vertrag(
        vertrag_id=str(uuid4()),
        haushalt_id=current_user.user_id,
        tarif_id=tarif_antrag.tarif_id,
        beginn_datum=date.today(),
        end_datum=date(MAXYEAR, 12, 31),  # oder ein spezifisches Enddatum
        jahresabschlag=tarif.grundgebuehr * 12  # Beispiel für Jahresabschlagberechnung
    )

    db.add(neuer_vertrag)
    await db.commit()
    await db.refresh(neuer_vertrag)

    logging_obj = schemas.LoggingSchema(
        user_id=current_user.user_id,
        endpoint="/tarifantrag",
        method="POST",
        message="Tarifantrag erfolgreich in Vertrag umgewandelt",
        success=True
    )
    logger.info(logging_obj.dict())

    return schemas.VertragResponse.from_orm(neuer_vertrag)




