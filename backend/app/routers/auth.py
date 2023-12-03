from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from sqlalchemy.future import select
from app import models, schemas, database, config


from app import schemas, database, models, hashing, oauth


router = APIRouter(prefix="/login", tags=["authentication"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.LoginResponse)
async def login(user_creds: schemas.NutzerLogin, db: AsyncSession = Depends(database.get_db_async)):
    try:
        stmt = select(models.Nutzer).where(models.Nutzer.email == user_creds.email)
        res = await db.execute(stmt)
        db_user = res.scalars().first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")
        if not hashing.Hashing.verify_password(user_creds.passwort, db_user.passwort):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwort falsch")

        access_token = oauth.create_access_token(data={"user_id": db_user.user_id})
        return {"access_token": access_token}
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Es gab folgenden Fehler: {e.orig}"
        else:
            msg = "Es gab einen Fehler bei der Registrierung."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
