import datetime
from pydantic import BaseModel, EmailStr, PastDate, field_validator, Field
from datetime import date
from typing import Dict, List, Optional
from app.types import Isolierungsqualitaet, AusrichtungDach, Rechnungsart


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


class RollenOverview(BaseModel):
    rolle: str
    count: int
      
      
class NutzerDateResponse(BaseModel):
    gestern: RollenOverview
    heute: RollenOverview

class EnergieberatendeCreate(BaseModel):
    spezialisierung: str

class EnergieberatendeResponse(BaseModel):
    user_id: int
    spezialisierung: str

class SolarteurCreate(BaseModel):
    pass

class SolarteurResponse(BaseModel):
    user_id: int

class HaushaltCreate(BaseModel):
    anzahl_bewohner: int
    heizungsart: str
    baujahr: int
    wohnflaeche: float
    isolierungsqualitaet: Isolierungsqualitaet
    ausrichtung_dach: AusrichtungDach
    dachflaeche: float
    energieeffizienzklasse: str

class HaushaltResponse(BaseModel):
    user_id: int
    anzahl_bewohner: int
    heizungsart: str
    baujahr: int
    wohnflaeche: float
    isolierungsqualitaet: Isolierungsqualitaet
    ausrichtung_dach: AusrichtungDach
    dachflaeche: float
    energieeffizienzklasse: str

class RechnungCreate(BaseModel):
    haushalt_id: int
    rechnungsbetrag: float
    rechnungsdatum: date
    faelligkeitsdatum: date
    rechnungsart: Rechnungsart
    zeitraum: Optional[date] = None

class RechnungResponse(BaseModel):
    rechnung_id: int
    haushalt_id: int
    rechnungsbetrag: float
    rechnungsdatum: date
    faelligkeitsdatum: date
    rechnungsart: Rechnungsart
    zeitraum: Optional[date] = None

    class Config:
        orm_mode = True

class TarifAntragCreate(BaseModel):
    haushalt_id: int
    tarif_id: int

class VertragResponse(BaseModel):
    vertrag_id: str
    haushalt_id: int
    tarif_id: int
    beginn_datum: date
    end_datum: date
    jahresabschlag: float
    vertragstatus: bool

    class Config:
        orm_mode = True


