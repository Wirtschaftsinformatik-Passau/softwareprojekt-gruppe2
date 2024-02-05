from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import schemas, models, database
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    """
    Erzeugt einen JWT (JSON Web Token) für die angegebenen Daten.

    Args:
        data (dict): Die Daten, die im Token gespeichert werden sollen.

    Returns:
        str: Der erstellte JWT.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    """
    Überprüft einen JWT (JSON Web Token) und gibt die darin enthaltenen Daten zurück, wenn der Token gültig ist.

    Args:
        token (str): Der zu überprüfende JWT.
        credentials_exception: Die Ausnahme, die ausgelöst wird, wenn die Überprüfung fehlschlägt.

    Returns:
        schemas.TokenData: Die in den JWT-Daten enthaltene Benutzer-ID.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(database.get_db_async)):
    """
    Holt den aktuellen Benutzer anhand des JWTs aus der Datenbank.

    Args:
        token (str): Der JWT des Benutzers.
        db (AsyncSession): Die Datenbankverbindung.

    Returns:
        models.Nutzer: Das Benutzermodell des aktuellen Benutzers.
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token, credentials_exception)
    stmt = (select(models.Nutzer).where(models.Nutzer.user_id == token_data.id)
            .where(or_(models.Nutzer.is_active == True, models.Nutzer.is_active.is_(None))))
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Nutzer nicht gefunden oder bereits deaktiviert",
                            headers={"WWW-Authenticate": "Bearer"})

    return user
