from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import exc
from sqlalchemy.future import select
from logging.config import dictConfig
import logging

from app import models, schemas, database, config, hashing
from app.logger import LogConfigBase, LogConfigAdresse, LogConfigRegistration


dictConfig(LogConfigRegistration().dict())
logger_registration = logging.getLogger("GreenEcoHubRegistration")

dictConfig(LogConfigAdresse().dict())
logger_adresse = logging.getLogger("GreenEcoHubAdresse")

dictConfig(LogConfigBase().dict())
logger_base = logging.getLogger("GreenEcoHubBase")


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/registration", status_code=status.HTTP_201_CREATED, response_model=schemas.NutzerResponse)
async def create_user(nutzer: schemas.NutzerCreate, db: AsyncSession = Depends(database.get_db_async)):
    try:
        nutzer.geburtsdatum = datetime.strptime(nutzer.geburtsdatum, "%a %b %d %Y").date()
        nutzer.rolle = models.Rolle(nutzer.rolle)
        email = nutzer.email
        nutzer.passwort = hashing.Hashing.hash_password(nutzer.passwort)
        stmt = select(models.Nutzer).where(models.Nutzer.email == email)
        res = await db.execute(stmt)
        if res.scalars().first() is not None:
            logging_msg = schemas.RegistrationLogging(user_id=0, role="unknown", msg=f"Email {email} bereits vergeben")
            logger_registration.error(logging_msg.dict())
            logger_base.error(logging_msg.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email bereits vergeben")

        db_user = models.Nutzer(**nutzer.dict())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logging_msg = schemas.RegistrationLogging(user_id=db_user.user_id, role=db_user.rolle.value, msg="User registered")
        logger_registration.info(logging_msg.dict())
        logger_base.info(logging_msg.dict())
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Es gab folgenden SQL Fehler: {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Error while registering user: {e.orig}"
            msg = "Es gab einen Fehler bei der Registrierung."

        logging_msg = schemas.RegistrationLogging(user_id=0, role="unknown", msg=logging_msg)
        logger_registration.error(logging_msg.dict())
        logger_base.error(logging_msg.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    return {"nutzer_id": db_user.user_id}


@router.post("/adresse", status_code=status.HTTP_201_CREATED, response_model=schemas.AdresseResponse)
async def create_adresse(adresse: schemas.AdresseCreate, db: AsyncSession = Depends(database.get_db_async)):
    try:
        db_adresse = models.Adresse(**adresse.dict())
        db.add(db_adresse)
        await db.commit()
        await db.refresh(db_adresse)
        logging_msg = schemas.AdresseLogging(adresse_id=db_adresse.adresse_id, msg="Adresse created")
        logger_adresse.info(logging_msg.dict())
        logger_base.info(logging_msg.dict())
        return {"adresse_id": db_adresse.adresse_id}
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Es gab folgenden Fehler: {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Error while registering user: {e.orig}"
            msg = "Es gab einen Fehler bei der Registrierung."
        logging_msg = schemas.AdresseLogging(adresse_id=0, msg=logging_msg)
        logger_adresse.error(logging_msg.dict())
        logger_base.error(logging_msg.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
