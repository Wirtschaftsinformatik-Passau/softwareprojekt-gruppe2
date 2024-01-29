from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import exc
from sqlalchemy.future import select
from logging.config import dictConfig
import logging
from time import sleep
from typing import List, Union, Optional
import uuid
from datetime import datetime, timedelta
from app import models, schemas, database, config, hashing, oauth
from app.logger import LogConfig, LogConfigAdresse, LogConfigRegistration
import uuid
from app.geo_utils import geocode_address
from app.email_sender import EmailSender
from app.config import settings


dictConfig(LogConfigRegistration().dict())
logger_registration = logging.getLogger("GreenEcoHubRegistration")

dictConfig(LogConfigAdresse().dict())
logger_adresse = logging.getLogger("GreenEcoHubAdresse")

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")

router = APIRouter(prefix="/users", tags=["Users"])

email_sender = EmailSender(
    smtp_server="132.231.36.210",
    smtp_port=1102,
    username="mailhog_grup2",
    password="connect19my41UP"
)


@router.post("/geocode", status_code=status.HTTP_200_OK)
async def geocode_entries(current_user: models.Nutzer = Depends(oauth.get_current_user),
                          db: AsyncSession = Depends(database.get_db_async)):
    try:
        stmt = select(models.Adresse)
        result = await db.execute(stmt)
        adressen = result.all()
        for adresse in adressen:
            if not adresse[0].latitude or not adresse[0].longitude:
                latitude, longitude = geocode_address(adresse[0].strasse, adresse[0].hausnummer, adresse[0].plz,
                                                      adresse[0].stadt)
                if latitude and longitude:
                    adresse[0].latitude = latitude
                    adresse[0].longitude = longitude
                    await db.commit()
                    await db.refresh(adresse[0])
                    logging_msg = f"Adresse {adresse[0].adresse_id} erfolgreich geocodiert"
                    logging_obj = schemas.LoggingSchema(user_id=current_user.user_id, endpoint="/geocode", method="POST",
                                                        message=logging_msg, success=True)
                    logger_adresse.info(logging_obj.dict())
                    sleep(0.5)
                else:
                    continue
        return {"msg": "Geocodierung erfolgreich"}

    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Error beim geocode Update {e.orig}"
            logging_msg = msg
        else:
            logging_msg = f"Error beim geocode Update: {e.orig}"
            msg = "Es gab einen Fehler bei der geocodierung."
        logging_obj = schemas.LoggingSchema(user_id=current_user.user_id, endpoint="/geocode", method="POST",
                                            message=logging_msg, success=False)
        logger.error(logging_obj.dict())
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    except Exception as e:
        logging_error = schemas.LoggingSchema(
            user_id=current_user.user_id,
            endpoint="/geocode",
            method="POST",
            message=f"Interner Serverfehler bei Geocodierung: {str(e)}",
            success=False
        )
        logger.error(logging_error.dict())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")


async def register_user(nutzer: schemas.NutzerCreate, db: AsyncSession):
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

        subject = "Willkommen bei GreenEcoHub!"
        body = f"Hallo {nutzer.vorname},\n\nVielen Dank für Ihre Anmeldung bei GreenEcoHub."
        await email_sender.send_email(nutzer.email, subject, body)

        user_id = db_user.user_id

        if nutzer.rolle == models.Rolle.Netzbetreiber:
            rollen_table = models.Netzbetreiber(user_id=user_id)
            db.add(rollen_table)
            await db.commit()
            await db.refresh(rollen_table)

        logging_msg = schemas.RegistrationLogging(user_id=db_user.user_id, role=db_user.rolle.value,
                                                  msg="User registriert")
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

    return db_user.user_id


@router.post("/registration", status_code=status.HTTP_201_CREATED, response_model=schemas.NutzerResponse)
async def create_user(nutzer: schemas.NutzerCreate, db: AsyncSession = Depends(database.get_db_async)):
    user_id: int = await register_user(nutzer, db)

    return {"nutzer_id": user_id}


@router.post("/adresse", status_code=status.HTTP_201_CREATED, response_model=schemas.AdresseIDResponse)
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


@router.get("/adresse", status_code=status.HTTP_200_OK,
            response_model=Union[List[schemas.AdresseResponse], List[schemas.AdresseResponseLongLat]])
async def get_adressen(skip: int = 0, limit: int = 100, type: str = "geo",
                       db: AsyncSession = Depends(database.get_db_async)):
    # TODO nur die adressen die im vertrag auch sind!!
    stmt = select(models.Adresse).offset(skip).limit(limit)
    result = await db.execute(stmt)
    adressen = result.all()

    if type == "geo":
        adressen_out = []
        for adresse in adressen:
            if adresse[0].longitude is None or adresse[0].latitude is None:
                continue
            else:
                adressen_out.append({
                    "id": adresse[0].adresse_id,
                    "position": [adresse[0].latitude, adresse[0].longitude],
                    "name": str(adresse[0].adresse_id)
                })

    else:
        adressen_out = [{
            "adresse_id": adresse[0].adresse_id,
            "strasse": adresse[0].strasse,
            "stadt": adresse[0].stadt,
            "hausnummer": adresse[0].hausnummer,
            "plz": adresse[0].plz,
            "land": adresse[0].land
        } for adresse in adressen]

    return adressen_out


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: int, db: AsyncSession = Depends(database.get_db_async)):
    stmt = select(models.Nutzer, models.Adresse).join(models.Adresse,
                                                      models.Nutzer.adresse_id == models.Adresse.adresse_id).where(
        models.Nutzer.user_id == id)
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
async def read_current_user(include_adresse: str = "yes",
                            current_user: models.Nutzer = Depends(oauth.get_current_user),
                            db: AsyncSession = Depends(database.get_db_async)):
    if include_adresse:
        user_id = current_user.user_id
        stmt = select(models.Nutzer, models.Adresse).join(models.Adresse,
                                                          models.Nutzer.adresse_id == models.Adresse.adresse_id).where(
            models.Nutzer.user_id == user_id)
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

    else:
        return current_user


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(id: int, updated_user: schemas.NutzerUpdate, db: AsyncSession = Depends(database.get_db_async)):
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

        changes = {}
        for field in ["email", "adresse_id", "vorname", "nachname", "geburtsdatum", "telefonnummer", "rolle",
                      "passwort"]:
            new_value = getattr(updated_user, field, None)

            # Setzen Sie den Wert auf None, wenn er leer ist, außer für das E-Mail-Feld
            if field != "email" and new_value == "":
                new_value = None

            # Behandeln Sie leere E-Mail-Strings speziell
            if field == "email" and new_value == "":
                new_value = db_user.email

            if new_value is not None and new_value != getattr(db_user, field):
                if field == "passwort" and new_value:
                    new_value = hashing.Hashing.hash_password(new_value)
                if field == "geburtsdatum" and new_value:
                    try:
                        new_value = datetime.strptime(new_value, "%Y-%m-%d").date()
                    except ValueError:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungültiges Datum")

                changes[field] = {"old": getattr(db_user, field), "new": new_value}
                setattr(db_user, field, new_value)

        # Update Rolle, falls sie geändert wurde und nicht leer ist
        if updated_user.rolle and updated_user.rolle != db_user.rolle:
            try:
                db_user.rolle = models.Rolle(updated_user.rolle)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        await db.commit()
        await db.refresh(db_user)

        if changes:
            logging_info = schemas.LoggingSchema(
                user_id=id,
                endpoint=f"/users/{id}",
                method="PUT",
                message=f"Änderungen an Nutzerdaten: {changes}",
                success=True
            )
            logger.info(logging_info.dict())

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
async def get_users(skip: int = 0, limit: int | None = None,
                    current_user: models.Nutzer = Depends(oauth.get_current_user),
                    db: AsyncSession = Depends(database.get_db_async)):
    stmt = (
        select(models.Nutzer, models.Adresse)
        .join(models.Adresse, models.Nutzer.adresse_id == models.Adresse.adresse_id)
        .offset(skip)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
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


@router.post("/request-password-reset")
async def request_password_reset(request: schemas.PasswortReqReset, db: AsyncSession = Depends(database.get_db_async)):
    """
    Sendet einen Link zum Zurücksetzen des Passworts an die E-Mail des Benutzers, wenn die angegebene E-Mail
    registriert ist.

    Parameters:
    - email (str): Die E-Mail-Adresse des Benutzers, der eine Kennwortrücksetzung beantragt.
    - db (AsyncSession): Die Datenbanksitzung zur Durchführung asynchroner Datenbankoperationen.

    Returns:
    - str: Eine Meldung, die angibt, ob ein Link zum Zurücksetzen des Passworts gesendet wurde.
    """
    email = request.email
    try:
        result = await db.execute(select(models.Nutzer).filter(models.Nutzer.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return "Wenn Ihre E-Mail registriert ist, wird ein Wiederherstellungslink gesendet."

        reset_token = await generate_password_reset_token()
        await store_reset_token(user.user_id, reset_token, db)

        await send_password_recovery_email(email, reset_token)

        return "Wenn Ihre E-Mail registriert ist, wird ein Wiederherstellungslink gesendet."

    except Exception as e:
        logger.error(f"Fehler in request_password_reset: {e}")
        raise HTTPException(status_code=500, detail="Interner Serverfehler")


async def generate_password_reset_token():
    return str(uuid.uuid4())


async def store_reset_token(user_id, token, db):
    try:
        expiration_time = datetime.now() + timedelta(hours=24)
        reset_token = models.PasswortResetToken(user_id=user_id, token=token, expiration=expiration_time)
        db.add(reset_token)
        await db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Fehler beim Speichern des Reset-Tokens: {e}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Interner Serverfehler")


async def send_password_recovery_email(user_email, token):
    subject = "Passwort-Wiederherstellung"
    recovery_link = f"132.231.36.102/reset-password/{token}"
    body = f"Bitte klicken Sie auf den Link, um Ihr Passwort zurückzusetzen: {recovery_link}"

    try:
        await email_sender.send_email(user_email, subject, body)
    except Exception as e:
        logger.error(f"Fehler beim Senden einer Wiederherstellungs-E-Mail: {e}")


@router.post("/reset-passwort/{token}")
async def reset_passwort(token: str, reset_data: schemas.PasswortReset,
                         db: AsyncSession = Depends(database.get_db_async)):
    """
    Setzt das Passwort des Benutzers zurück, wenn das angegebene Token gültig und nicht abgelaufen ist.

    Parameters:
    - token (str): Das Token zum Zurücksetzen des Passworts, das dem Benutzer zur Verfügung gestellt wurde.
    - neu_passwort (str): Das neue Kennwort, das der Benutzer festlegen möchte.
    - db (AsyncSession): Die Datenbanksitzung für die Durchführung asynchroner Datenbankoperationen.

    Returns:
    - str: Eine Nachricht, die das Ergebnis des Vorgangs zum Zurücksetzen des Kennworts angibt.

    Raises:
    - ValueError: Wenn das Token ungültig oder abgelaufen ist, oder wenn der mit dem Token verknüpfte Benutzer
                  nicht gefunden wird.
    - SQLAlchemyError: Wenn während des Vorgangs ein datenbankbezogener Fehler auftritt.
    - Exception: Für alle anderen unerwarteten Fehler, die auftreten können.
    """
    try:
        result = await db.execute(select(models.PasswortResetToken).filter(models.PasswortResetToken.token == token))
        token_data = result.scalar_one_or_none()
        if not token_data:
            await db.rollback()
            logging_error = schemas.LoggingSchema(
                user_id=0,
                endpoint="/users/reset-passwort/" + token,
                method="POST",
                message=f"Ungültiger Token: {token}",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungültiger Token")

        if token_data.expiration < datetime.utcnow():
            await db.rollback()
            logging_error = schemas.LoggingSchema(
                user_id=0,
                endpoint="/users/reset-passwort/" + token,
                method="POST",
                message=f"Token abgelaufen: {token}",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token abgelaufen")
            raise ValueError("Ungültiger Token")

        if token_data.expiration < datetime.utcnow():
            raise ValueError("Token abgelaufen")

        hashed_passwort = hashing.Hashing.hash_password(reset_data.neu_passwort)

        result = await db.execute(select(models.Nutzer).filter(models.Nutzer.user_id == token_data.user_id))
        nutzer = result.scalar_one_or_none()

        if not nutzer:
            await db.rollback()
            logging_error = schemas.LoggingSchema(
                user_id=0,
                endpoint="/users/reset-passwort/" + token,
                method="POST",
                message=f"Nutzer nicht gefunden: {token_data.user_id}",
                success=False
            )
            logger.error(logging_error.dict())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")

        nutzer.passwort = hashed_passwort
        await db.commit()
        await db.refresh(nutzer)

        await db.delete(token_data)
        await db.commit()

        logging_info = schemas.LoggingSchema(
            user_id=nutzer.user_id,
            endpoint="/users/reset-passwort/" + token,
            method="POST",
            message="Passwort erfolgreich zurückgesetzt",
            success=True
        )
        logger.info(logging_info.dict())
        return "Passwort erfolgreich zurückgesetzt"

    except ValueError as ve:
        return str(ve)

    except SQLAlchemyError as e:
        await db.rollback()
        return f"Datenbankfehler aufgetreten: {e}"

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        await db.rollback()
        return f"Ein unerwarteter Fehler ist aufgetreten: {e}"


@router.post("/chat/send", response_model=schemas.ChatMessageSendResponse, status_code=status.HTTP_201_CREATED)
async def send_message(chat_message: schemas.ChatMessageCreate, db: AsyncSession = Depends(database.get_db_async)):
    neue_nachricht = models.ChatMessage(**chat_message.dict())
    db.add(neue_nachricht)
    await db.commit()
    await db.refresh(neue_nachricht)
    return {"nachricht": "Nachricht erfolgreich gesendet", "nachricht_id": neue_nachricht.nachricht_id}


@router.get("/chat/history", response_model=List[schemas.ChatMessageResponse], status_code=status.HTTP_200_OK)
async def get_chat_history(user_id: int, other_user_id: Optional[int] = None, db: AsyncSession = Depends(database.get_db_async)):
    query = select(models.ChatMessage).where(
        (models.ChatMessage.sender_id == user_id) | (models.ChatMessage.empfaenger_id == user_id))

    if other_user_id:
        query = query.where(
            (models.ChatMessage.sender_id == other_user_id) | (models.ChatMessage.empfaenger_id == other_user_id))

    result = await db.execute(query)
    chat_history = result.scalars().all()

    return chat_history
