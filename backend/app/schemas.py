import datetime
from pydantic import BaseModel, EmailStr, PastDate, field_validator
from datetime import date
from typing import Dict, List


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
        if datetime.datetime.strptime(v, "%Y-%m-%d").date() > date.today():
            raise ValueError('geburtsdatum darf nicht in der Zukunft liegen')
        return v

    telefonnummer: str
    rolle: str


class NutzerResponse(BaseModel):
    nutzer_id: int


class TokenRenew(BaseModel):
    access_token: str


class NutzerLogin(BaseModel):
    email: EmailStr
    passwort: str


class TokenResponse(BaseModel):
    access_token: str


class LoggingSchema(BaseModel):
    user_id: int
    endpoint: str
    method: str
    message: str
    success: bool


class RegistrationLogging(BaseModel):
    user_id: int
    role: str
    msg: str = f"User registered"


class AdresseLogging(BaseModel):
    adresse_id: int
    msg: str = f"Adresse created"
class UserOut(BaseModel):
    user_id: int
    email: EmailStr
    adresse_id: int
    vorname: str
    nachname: str
    geburtsdatum: str
    telefonnummer: str
    rolle: str

    class Config:
        from_attributes = True

class UsersOut(BaseModel):
    users: list[UserOut]
    count: int


class AdminDashboardResponse(BaseModel):
    Log_Daten: Dict[str, int]
    users_id: List[int]


