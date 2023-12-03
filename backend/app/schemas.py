from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from app.models import AenderungsartEnum


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
        if datetime.strptime(v, "%d.%m.%Y").date() > date.today():
            raise ValueError('geburtsdatum darf nicht in der Zukunft liegen')
        return v

    telefonnummer: str


class NutzerResponse(BaseModel):
    nutzer_id: int


class NutzerLogin(BaseModel):
    email: EmailStr
    passwort: str


class LogBase(BaseModel):
    zeitpunkt: datetime
    aenderungsart: AenderungsartEnum


class Log(LogBase):
    log_id: int
    user_id: int


class StromtarifCreate(BaseModel):
    tarifname: str
    preis_pro_kwh: float
    grundgebuehr: float
    laufzeit: int

    @field_validator('preis_pro_kwh')
    def validate_preis_pro_kwh(cls, v):
        if v < 0:
            raise ValueError("Negative Preise sind nicht zulässig.")
        return v


class StromtarifResponse(BaseModel):
    tarif_id: int


class VertragCreate(BaseModel):
    beginn_datum: date
    end_datum: date
    tarif_id: int
    haushalt_id: int

    @field_validator('end_datum')
    def enddatum_must_be_later(cls, v, values):
        if 'startdatum' in values and v <= values['startdatum']:
            raise ValueError('Enddatum muss nach dem Startdatum liegen')
        return v


class VertragResponse(BaseModel):
    vertrag_id: int