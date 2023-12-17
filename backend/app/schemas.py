import datetime
from pydantic import BaseModel, EmailStr, PastDate, field_validator, Field
from datetime import date
from typing import Dict, List


class AdresseCreate(BaseModel):
    strasse: str
    hausnummer: int
    zusatz: str = None
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


class TokenData(BaseModel):
    id: int


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


class AdminDashboardResponse(BaseModel):
    Log_Daten: Dict[str, int]
    users_id: List[int]


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


class ChartData(BaseModel):
    x: str
    y: int

    class Config:
        from_attributes = True


class PieChartData(BaseModel):
    id: str
    label: str
    value: int

    class Config:
        from_attributes = True


class BarChartData(BaseModel):
    date: str
    value: int

    class Config:
        from_attributes = True


class ChartDataCategorical(BaseModel):
    id: str
    data: List[ChartData]


class LogEntry(BaseModel):
    log_id: int
    timestamp: str
    level: str
    name: str
    message: str
    user_id: int
    endpoint: str
    method: str
    success: bool

    class Config:
        from_attributes = True


class TarifCreate(BaseModel):
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str


class TarifResponse(BaseModel):
    tarif_id: int
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str

    class Config:
        from_attributes = True


class PreisstrukturenCreate(BaseModel):
    bezugspreis_kwh: float
    einspeisung_kwh: float

    @field_validator('bezugspreis_kwh', 'einspeisung_kwh')
    def check_positive_value(cls, v):
        if v < 0:
            raise ValueError('Der Wert darf nicht negativ sein')
        return v


class PreisstrukturenResponse(BaseModel):
    preis_id: int


class AggregatedDashboardSmartMeterData(BaseModel):
    datum: str
    gesamt_pv_erzeugung: float = Field(..., description="Gesamtleistung der PV-Anlagen")
    gesamt_soc: float = Field(..., description="Durchschnittlicher SOC aller Speicher")
    gesamt_batterie_leistung: float = Field(..., description="Gesamtleistung der Batterien")
    gesamt_last: float = Field(..., description="Gesamtlastverbrauch")


class DashboardSmartMeterDataResponse(BaseModel):
    message: str


class PVAnlageBase(BaseModel):
    modultyp: str
    kapazitaet: float
    installationsflaeche: float
    installationsdatum: str
    installationsstatus: str
    modulanordnung: str
    kabelwegfuehrung: str
    montagesystem: str
    schattenanalyse: str
    wechselrichterposition: str
    installationsplan: str


class PVAnlageCreate(PVAnlageBase):
    haushalt_id: int
    solarteur_id: int
    netzbetreiber_id: int


class PVAnlage(PVAnlageBase):
    anlage_id: int
    prozess_status: str
    nvpruefung_status: bool

    class Config:
        from_attributes = True


class NetzvertraeglichkeitspruefungResponse(BaseModel):
    anlage_id: int
    nvpruefung_status: bool


class EinspeisezusageResponse(BaseModel):
    message: str
    anlage_id: int


class RollenOverview(BaseModel):
    rolle: str
    count: int
      
      
class NutzerDateResponse(BaseModel):
    gestern: RollenOverview
    heute: RollenOverview
