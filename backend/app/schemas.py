from pydantic import BaseModel, EmailStr


class AdresseCreate(BaseModel):
    strasse: str
    hausnummer: int
    zusatz: str
    plz: int
    stadt: str
    land: str


class UserCreate(BaseModel):
    email: EmailStr
    adresse: AdresseCreate
