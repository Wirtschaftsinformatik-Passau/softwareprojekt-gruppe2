import datetime
from pydantic import BaseModel, EmailStr, PastDate, field_validator, Field, Extra, PositiveInt, constr
from datetime import date
from typing import Dict, List, Optional
from app.types import *

from app.types import ProzessStatus, Montagesystem, Schatten, Orientierung, AusweisStatus, Vertragsstatus


class AdresseCreate(BaseModel):
    strasse: str
    hausnummer: int
    zusatz: str = None
    plz: int
    stadt: str
    land: str


class AdresseIDResponse(BaseModel):
    adresse_id: int


class AdresseResponse(BaseModel):
    adresse_id: int
    strasse: str
    stadt: str
    plz: int
    hausnummer: int
    land: str

    class Config:
        from_attributes = True


class AdresseResponseLongLat(BaseModel):
    id: int
    position: List[float]
    name: str

    class Config:
        from_attributes = True


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

    class Config:
        extra = Extra.allow


class TarifResponse(BaseModel):
    tarif_id: int
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str

    # class Config:
    # orm_mode = True


class TarifResponseAll(BaseModel):
    netzbetreiber_id: int
    tarif_id: int
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str


class TarifHaushaltResponse(BaseModel):
    vorname: str
    nachname: str
    email: str
    tarif_id: int
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str


class PreisstrukturenCreate(BaseModel):
    bezugspreis_kwh: float
    einspeisung_kwh: float

    @field_validator('bezugspreis_kwh', 'einspeisung_kwh')
    def check_positive_value(cls, v):
        if v < 0:
            raise ValueError('Der Wert darf nicht negativ sein')
        return v

    class Config:
        extra = Extra.allow


class PreisstrukturenResponse(BaseModel):
    preis_id: int
    bezugspreis_kwh: float
    einspeisung_kwh: float


class AggregatedDashboardSmartMeterData(BaseModel):
    datum: str
    gesamt_pv_erzeugung: float = Field(..., description="Gesamtleistung der PV-Anlagen")
    gesamt_soc: float = Field(..., description="Durchschnittlicher SOC aller Speicher")
    gesamt_batterie_leistung: float = Field(..., description="Gesamtleistung der Batterien")
    gesamt_last: float = Field(..., description="Gesamtlastverbrauch")


class AggregatedDashboardSmartMeterDataResponseSOC(BaseModel):
    x: str
    y: float = Field(..., description="Durchschnittlicher SOC aller Speicher")


class AggregatedDashboardSmartMeterDataResponsePV(BaseModel):
    x: str
    y: float = Field(..., description="Gesamtleistung der PV-Anlagen")


class AggregatedDashboardSmartMeterDataResponseBatterie(BaseModel):
    x: str
    y: float = Field(..., description="Gesamtleistung der Batterien")


class AggregatedDashboardSmartMeterDataResponseLast(BaseModel):
    x: str
    y: float = Field(..., description="Gesamtlastverbrauch")


class DashboardSmartMeterDataResponse(BaseModel):
    message: str


field_to_schema_mapping = {
    "all": AggregatedDashboardSmartMeterData,
    "soc": AggregatedDashboardSmartMeterDataResponseSOC,
    "pv": AggregatedDashboardSmartMeterDataResponsePV,
    "batterie": AggregatedDashboardSmartMeterDataResponseBatterie,
    "last": AggregatedDashboardSmartMeterDataResponseLast
}


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


class PVAnlageAnfrage(BaseModel):
    haushalt_id: int


class PVAnforderungResponse(BaseModel):
    anlage_id: int
    prozess_status: ProzessStatus


class PVSolarteuerResponse(BaseModel):
    anlage_id: int
    prozess_status: ProzessStatus
    vorname: str
    nachname: str
    email: str
    strasse: str
    hausnummer: int
    plz: int
    stadt: str



class TarifLaufzeitResponse(BaseModel):
    laufzeit: int
    value: int


class AngebotCreate(BaseModel):
    anlage_id: int
    modultyp: str
    kapazitaet: float
    installationsflaeche: float
    modulanordnung: Orientierung
    kosten: float


class AngebotResponse(BaseModel):
    angebot_id: int
    anlage_id: int
    kosten: float

    class Config:
        from_attributes = True


class InstallationsplanCreate(BaseModel):
    kabelwegfuehrung: str
    montagesystem: Montagesystem
    schattenanalyse: Schatten
    wechselrichterposition: str
    installationsdatum: date


class InstallationsplanResponse(BaseModel):
    installationsplan: str


class PVAngebotResponse(BaseModel):
    modultyp: str
    kapazitaet: float
    installationsflaeche: float


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
    ausrichtung_dach: Orientierung
    dachflaeche: float
    energieeffizienzklasse: str


class HaushaltResponse(BaseModel):
    user_id: int
    anzahl_bewohner: int
    heizungsart: str
    baujahr: int
    wohnflaeche: float
    isolierungsqualitaet: Isolierungsqualitaet
    ausrichtung_dach: Orientierung
    dachflaeche: float
    energieeffizienzklasse: str


class RechnungCreate(BaseModel):
    user_id: int
    rechnungsbetrag: float
    rechnungsdatum: date
    faelligkeitsdatum: date
    rechnungsart: Rechnungsart
    zeitraum: Optional[date] = None

    class Config:
        extra = Extra.allow


class VertragPreview(BaseModel):
    beginn_datum: date
    end_datum: date
    jahresabschlag: float


class RechnungResponse(BaseModel):
    rechnung_id: int
    user_id: int
    rechnungsbetrag: float
    rechnungsdatum: date
    faelligkeitsdatum: date
    rechnungsart: Rechnungsart
    zeitraum: Optional[date] = None

    class Config:
        extra = Extra.allow


class TarifAntragCreate(BaseModel):
    user_id: int
    tarif_id: int
    beginn_datum: date
    end_datum: date
    jahresabschlag: float
    netzbetreiber_id: int
    vertragstatus: Vertragsstatus


class VertragResponse(BaseModel):
    vertrag_id: int
    user_id: int
    tarif_id: int
    beginn_datum: date
    end_datum: date
    jahresabschlag: float
    vertragstatus: Vertragsstatus


class VertragTarifResponse(BaseModel):
    vertrag_id: int
    netzbetreiber_id: int
    user_id: int
    tarif_id: int
    beginn_datum: date
    end_datum: date
    jahresabschlag: float
    vertragstatus: Vertragsstatus
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str


class VertragTarifResponseStatus(BaseModel):
    vertrag_id: int
    netzbetreiber_id: int
    user_id: int
    tarif_id: int
    beginn_datum: date
    end_datum: date
    jahresabschlag: float
    vertragstatus: Vertragsstatus
    tarifname: str
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    spezielle_konditionen: str
    vertragstatus: Vertragsstatus


class VertragTarifNBResponse(BaseModel):
    vorname: str
    nachname: str
    email: str
    vertrag_id: int
    netzbetreiber_id: int
    tarif_id: int
    beginn_datum: date
    end_datum: date
    jahresabschlag: float
    vertragstatus: Vertragsstatus
    preis_kwh: float
    grundgebuehr: float
    laufzeit: int
    tarifname: str
    spezielle_konditionen: str


class KalenderEintragCreate(BaseModel):
    zeitpunkt: date
    user_id: int
    beschreibung: str


class KalenderEintrag(KalenderEintragCreate):
    kalender_id: int

    class Config:
        from_attributes = True


class EnergieausweisAnfrage(BaseModel):
    pass


class EnergieausweisAnfrageResponse(BaseModel):
    energieausweis_id: int
    haushalt_id: int
    energieberater_id: int
    ausweis_status: AusweisStatus

    class Config:
        from_attributes = True


class AngebotAnnahmeResponse(BaseModel):
    angebot_id: int
    anlage_id: int
    kosten: float
    angebotstatus: bool
    created_at: str

    class Config:
        from_attributes = True


class AngebotVorschlag(BaseModel):
    anlage_id: int = None
    haushalt_id: int = None
    solarteur_id: int = None
    modultyp: Optional[str] = None
    kapazitaet: Optional[float] = None
    installationsflaeche: Optional[float] = None
    installationsdatum: Optional[date] = None
    modulanordnung: Optional[Orientierung] = None
    kabelwegfuehrung: Optional[str] = None
    montagesystem: Optional[Montagesystem] = None
    schattenanalyse: Optional[Schatten] = None
    wechselrichterposition: Optional[str] = None
    installationsplan: Optional[str] = None
    prozess_status: ProzessStatus = None
    nvpruefung_status: Optional[bool] = None


class DatenanfrageResponse(BaseModel):
    message: str
    haushalt_id: int
    anfragestatus: bool


class HaushaltsDatenFreigabe(BaseModel):
    anzahl_bewohner: int
    heizungsart: str
    baujahr: int
    wohnflaeche: float
    isolierungsqualitaet: Isolierungsqualitaet
    ausrichtung_dach: Orientierung
    dachflaeche: float
    energieeffizienzklasse: str


class DashboardAggregatedData(BaseModel):
    gesamt_pv_erzeugung: float
    durchschnitt_soc: float
    gesamt_batterie_leistung: float
    gesamt_last: float


class HaushaltsDatenFreigabeResponse(BaseModel):
    message: str
    haushaltsdaten: HaushaltsDatenFreigabe
    dashboard_daten: DashboardAggregatedData


class PVAnlageResponse(BaseModel):
    anlage_id: int
    solarteur_id: Optional[int] = None


class PVAnlageHaushaltResponse(BaseModel):
    anlage_id: int
    haushalt_id: int
    solarteur_id: int
    prozess_status: ProzessStatus
    nvpruefung_status: Optional[bool] | str = "Noch nicht geprüft"


class EnergieausweiseUpdate(BaseModel):
    energieeffizienzklasse: str
    verbrauchskennwerte: float


class EnergieeffizienzmassnahmenCreate(BaseModel):
    massnahmetyp: MassnahmeTyp
    einsparpotenzial: float
    kosten: float


class EnergieausweisCreate(BaseModel):
    ausstellungsdatum: date
    gueltigkeit: date


class EnergieausweisCreateResponse(BaseModel):
    message: str
    ausweis_status: str


class PVAnlageAbnahmeResponse(BaseModel):
    message: str
    anlage_id: int
    prozess_status: str

class KündigungsanfrageCreate(BaseModel):
    vertrag_id: int

class KündigungsanfrageResponse(BaseModel):
    anfrage_id: int
    vertrag_id: int
    bestätigt: bool

class VertragUpdateStatus(BaseModel):
    vertragstatus: Vertragsstatus
