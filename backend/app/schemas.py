import datetime
from pydantic import BaseModel, EmailStr, PastDate, field_validator
from datetime import date


class AdresseCreate(BaseModel):
    strasse: str
    hausnummer: int
    zusatz: str | None = None
    plz: int
    stadt: str
    land: str


class AdresseResponse(BaseModel):
    adresse_id: int


class NutzerCreate(BaseModel):
    email: EmailStr
    adresse_id: int
    vorname: str
    nachname: str
    passwort: str
    geburtsdatum: str
    @field_validator('geburtsdatum')
    def check_geburtsdatum(cls, v):
        if datetime.datetime.strptime(v, "%a %b %d %Y").date() > date.today():
            raise ValueError('geburtsdatum darf nicht in der Zukunft liegen')
        return v

    telefonnummer: str
    rolle: str


class NutzerResponse(BaseModel):
    nutzer_id: int


class NutzerLogin(BaseModel):
    email: EmailStr
    passwort: str


class LoginResponse(BaseModel):
    access_token: str


