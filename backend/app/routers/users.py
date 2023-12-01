from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()


@router.post("/registration/", response_model=schemas.UserCreate)
def create_user(user: schemas.UsersCreate, db: Session = Depends(database.get_db)):
    db_adresse = models.Adresse(**adresse.dict())
    db.add(db_adresse)
    db.commit()
    db.refresh(db_adresse)
    return db_adresse
