from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import exc
from sqlalchemy.future import select
from logging.config import dictConfig
import logging

from app import models, schemas, database, config, hashing, oauth
from app.logger import LogConfig, LogConfigAdresse, LogConfigRegistration


dictConfig(LogConfigRegistration().dict())
logger_registration = logging.getLogger("GreenEcoHubRegistration")

dictConfig(LogConfigAdresse().dict())
logger_adresse = logging.getLogger("GreenEcoHubAdresse")

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/registration", status_code=status.HTTP_201_CREATED, response_model=schemas.NutzerResponse)
async def create_user(nutzer: schemas.NutzerCreate, db: AsyncSession = Depends(database.get_db_async)):
    try:
        nutzer.geburtsdatum = datetime.strptime(nutzer.geburtsdatum, "%Y-%m-%d").date()
        try:
            nutzer.rolle = models.Rolle(nutzer.rolle)
        except ValueError as e:
            if config.settings.DEV:
                msg = f"Error beim User Update {e}"
                logging_msg = msg
            else:
                logging_msg = f"Error beim : {e}"
                msg = "Es gab einen Fehler bei der Registrierung."
            logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/users/registration", method="POST",
                                                message=logging_msg, success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        email = nutzer.email
        nutzer.passwort = hashing.Hashing.hash_password(nutzer.passwort)
        stmt = select(models.Nutzer).where(models.Nutzer.email == email)
        res = await db.execute(stmt)
        if res.scalars().first() is not None:
            logging_msg = schemas.RegistrationLogging(user_id=0, role="unknown", msg=f"Email {email} bereits vergeben")
            logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/users/registration", method="POST",
                                                message=f"Email {email} bereits vergeben", success=False)
            logger_registration.error(logging_msg.dict())
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email bereits vergeben")

        db_user = models.Nutzer(**nutzer.dict())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logging_msg = schemas.RegistrationLogging(user_id=db_user.user_id, role=db_user.rolle.value, msg="User registriert")
        logging_obj = schemas.LoggingSchema(user_id=db_user.user_id, endpoint="/users/registration", method="POST",
                                            message="User registriert", success=True)
        logger_registration.info(logging_msg.dict())
        logger.info(logging_obj.dict())
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Es gab folgenden SQL Fehler: {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Error while registering user: {e.orig}"
            msg = "Es gab einen Fehler bei der Registrierung."

        logging_obj = schemas.LoggingSchema(user_id=0, endpoint="/users/registration", method="POST",
                                            message=logging_msg, success=False)
        logging_msg = schemas.RegistrationLogging(user_id=0, role="unknown", msg=logging_msg)
        logger_registration.error(logging_msg.dict())
        logger.error(logging_obj.dict())
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


@router.get("/adresse", status_code=status.HTTP_200_OK)
async def get_adressen(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db_async)):
    stmt = select(models.Adresse).offset(skip).limit(limit)
    result = await db.execute(stmt)
    adressen = result.all()
    adressen_out = [{
        "adresse_id": adresse[0].adresse_id,
        "strasse": adresse[0].strasse,
        "stadt": adresse[0].stadt,
        "plz": adresse[0].plz,
        "land": adresse[0].land
    } for adresse in adressen]
    return adressen_out

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: int, db: AsyncSession = Depends(database.get_db_async)):
    stmt = select(models.Nutzer, models.Adresse).join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id).where(models.Nutzer.user_id == id)
    result = await db.execute(stmt)
    user_adresse_pair = result.first()
    try:
        user = user_adresse_pair[0]
    except TypeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nicht gefunden")
    adresse = user_adresse_pair[1]
    user_out = {
        "nachname": user.nachname,
        "email": user.email,
        "user_id": user.user_id,
        "vorname": user.vorname,
        "rolle": user.rolle,
        "adresse_id": user.adresse_id,
        "geburtsdatum": user.geburtsdatum,
        "telefonnummer": user.telefonnummer,
        "strasse": adresse.strasse,
        "stadt": adresse.stadt,
        "hausnr": adresse.hausnummer,
        "plz": adresse.plz,

    }
    return user_out
@router.put("/adresse/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_adresse(id: int, adresse: schemas.AdresseCreate, db: AsyncSession = Depends(database.get_db_async)):
    stmt = select(models.Adresse).where(models.Adresse.adresse_id == id)
    result = await db.execute(stmt)
    db_adresse = result.first()

    if db_adresse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adresse nicht gefunden")
    db_adresse.strasse = adresse.strasse
    db_adresse.hausnummer = adresse.hausnummer
    db_adresse.zusatz = adresse.zusatz
    db_adresse.plz = adresse.plz
    db_adresse.stadt = adresse.stadt
    db_adresse.land = adresse.land
    await db.commit()
    await db.refresh(db_adresse)
    return {"adresse_id": db_adresse.adresse_id}

@router.get("/current/single", status_code=status.HTTP_200_OK)
async def read_current_user(current_user: models.Nutzer = Depends(oauth.get_current_user)):
    return current_user


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(id: int, user: schemas.NutzerCreate, db: AsyncSession = Depends(database.get_db_async)):
    stmt = select(models.Nutzer).where(models.Nutzer.user_id == id)
    try:
        result = await db.execute(stmt)
        try:
            db_user = result.first()[0]
        except TypeError:
            logging_obj = schemas.LoggingSchema(user_id=id, endpoint="/users/{id}", method="PUT",
                                                message="Nutzer nicht gefunden zum Bearbeiten", success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nicht gefunden")

        db_user.email = user.email
        db_user.adresse_id = user.adresse_id
        db_user.vorname = user.vorname
        db_user.nachname = user.nachname
        db_user.geburtsdatum = datetime.strptime(user.geburtsdatum, "%Y-%m-%d").date()
        db_user.telefonnummer = user.telefonnummer
        try:
            db_user.rolle = models.Rolle(user.rolle)
        except ValueError as e:
            if config.settings.DEV:
                msg = f"Error beim User Update {e}"
                logging_msg = msg
            else:
                logging_msg = f"Error beim User Update: {e}"
                msg = "Es gab einen Fehler bei der Registrierung."
            logging_obj = schemas.LoggingSchema(user_id=id, endpoint="/users/{id}", method="PUT",
                                                message=logging_msg, success=False)
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        if user.passwort:
            db_user.passwort = hashing.Hashing.hash_password(user.passwort)
        else:
            db_user.passwort = db_user.passwort

        await db.commit()
        await db.refresh(db_user)
        logging_obj = schemas.LoggingSchema(user_id=id, endpoint="/users/{id}", method="PUT",
                                            message="Nutzer erfolgreich bearbeitet", success=True)
        logger.info(logging_obj.dict())
        return {"user_id": db_user.user_id}
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Error beim User Update {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Error beim User Update: {e.orig}"
            msg = "Es gab einen Fehler bei der Registrierung."
        logging_obj = schemas.LoggingSchema(user_id=id, endpoint="/users/{id}", method="PUT",
                                            message=logging_msg, success=False)
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, limit: int = 100, current_user: models.Nutzer = Depends(oauth.get_current_user),
                    db: AsyncSession = Depends(database.get_db_async)):
    stmt = (
        select(models.Nutzer, models.Adresse)
        .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
        .offset(skip)
        .limit(limit)
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
            "geburtsdatum": user.geburtsdatum,
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: AsyncSession = Depends(database.get_db_async),
                      current_user: models.Nutzer = Depends(oauth.get_current_user)):
    try:
        if current_user.rolle != models.Rolle.Admin:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/users/{id}",
                method="DELETE",
                message=f"Zugriff verweigert: Nutzer {current_user.user_id} ist kein Admin",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nur Admins können Nutzer löschen")

        stmt = select(models.Nutzer).where(models.Nutzer.user_id == id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user:
            logging_obj = schemas.LoggingSchema(
                user_id=current_user.user_id,
                endpoint=f"/users/{id}",
                method="DELETE",
                message=f"Nutzer mit ID {id} nicht gefunden",
                success=False
            )
            logger.error(logging_obj.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")

        adresse_id = user.adresse_id
        await db.delete(user)
        await db.commit()

        # Überprüfung kann ausgelassen werden, ist drin für sehr unwahrscheinliche Szenarien
        other_users = await db.execute(select(models.Nutzer).where(models.Nutzer.adresse_id == adresse_id))
        if other_users.first() is None:
            adresse = await db.get(models.Adresse, adresse_id)
            if adresse:
                await db.delete(adresse)
                await db.commit()

        logging_obj = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint=f"/users/{id}",
            method="DELETE",
            message="Nutzer erfolgreich gelöscht",
            success=True
        )
        logger.info(logging_obj.dict())

    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/admin/logs",
            method="GET",
            message=f"Interner Serverfehler: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")