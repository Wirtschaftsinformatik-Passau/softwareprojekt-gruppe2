from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from sqlalchemy.future import select
from logging.config import dictConfig
import logging
from app import models, schemas, database, config
from app import schemas, database, models, hashing, oauth

from app.logger import LogConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.TokenResponse)
async def login(user_creds: schemas.NutzerLogin, db: AsyncSession = Depends(database.get_db_async)):
    """
    Authentifiziert einen Nutzer und gibt ein Token zurück.

    Args:
        user_creds (schemas.NutzerLogin): Die Nutzeranmeldeinformationen.
        db (AsyncSession, optional): Die Datenbank-Sitzung. Standardmäßig wird `database.get_db_async` verwendet.

    Returns:
        dict: Ein Token zur Authentifizierung des Nutzers.

    Raises:
        HTTPException: Wenn die Anmeldung fehlschlägt.
    """
    try:

        stmt = select(models.Nutzer).where(models.Nutzer.email == user_creds.email)
        res = await db.execute(stmt)
        db_user = res.scalars().first()
        if db_user is None:
            logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/auth/login", method="POST",
                                                message="User not found", success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")

        if not db_user.is_active:
            logging_obj = schemas.LoggingSchema(user_id=db_user.user_id, endpoint="/auth/login", method="POST",
                                                message="User not active", success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nutzer ist nicht aktiviert")

        if not hashing.Hashing.verify_password(user_creds.passwort, db_user.passwort):
            logging_obj = schemas.LoggingSchema(user_id=db_user.user_id, endpoint="/auth/login", method="POST",
                                                message="Wrong password", success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwort falsch")

        access_token = oauth.create_access_token(data={"user_id": db_user.user_id})
        logging_obj = schemas.LoggingSchema(user_id=db_user.user_id, endpoint="/auth/login", method="POST",
                                            message="User eingeloggt", success=True)
        logger.info(logging_obj.dict())
        return {"access_token": access_token}

    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Es gab folgenden Fehler: {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Es gab folgenden Fehler: {e.orig}"
            msg = "Es gab einen Fehler bei der Registrierung."

        logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/auth/login", method="POST",
                                            message=logging_msg, success=False)
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)



