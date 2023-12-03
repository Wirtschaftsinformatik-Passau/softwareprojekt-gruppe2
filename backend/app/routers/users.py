from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import exc
from sqlalchemy.future import select
from app import models, schemas, database, config

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/registration", status_code=status.HTTP_201_CREATED, response_model=schemas.NutzerResponse)
async def create_user(nutzer: schemas.NutzerCreate, db: AsyncSession = Depends(database.get_db_async)):
    nutzer.geburtsdatum = datetime.strptime(nutzer.geburtsdatum, "%d.%m.%Y").date()
    email = nutzer.email

    try:
        stmt = select(models.Nutzer).where(models.Nutzer.email == email)
        res = await db.execute(stmt)
        if res.scalars().first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email bereits vergeben")

        db_user = models.Nutzer(**nutzer.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except exc.IntegrityError as e:
        if config.settings.DEV:
            msg = f"Es gab folgenden Fehler: {e.orig}"
        else:
            msg = "Es gab einen Fehler bei der Registrierung."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    return {"nutzer_id": db_user.user_id}


@router.post("/adresse", status_code=status.HTTP_201_CREATED, response_model=schemas.AdresseResponse)
async def create_adresse(adresse: schemas.AdresseCreate, db: AsyncSession = Depends(database.get_db_async)):
    db_adresse = models.Adresse(**adresse.model_dump())
    db.add(db_adresse)
    await db.commit()
    await db.refresh(db_adresse)
    return {"adresse_id": db_adresse.adresse_id}
