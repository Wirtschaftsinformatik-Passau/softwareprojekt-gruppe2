from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Enum, ForeignKey, \
    Identity, TIMESTAMP, func

from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.config import settings
from app.types import Rolle, Isolierungsqualitaet, AusrichtungDach, Rechnungsart


class Adresse(Base):
    __tablename__ = 'adresse' if settings.OS == 'Linux' else "Adresse"

    adresse_id = Column(Integer, Identity(), primary_key=True)
    strasse = Column(String)
    hausnummer = Column(Integer)
    zusatz = Column(String)
    plz = Column(Integer)
    stadt = Column(String)
    land = Column(String)


class Nutzer(Base):
    __tablename__ = 'nutzer' if settings.OS == 'Linux' else "Nutzer"
    user_id = Column(Integer, Identity(), primary_key=True)
    nachname = Column(String)
    vorname = Column(String)
    geburtsdatum = Column(Date)
    email = Column(String)
    passwort = Column(String)
    rolle = Column(Enum(Rolle), ENUM(*[r.value for r in Rolle],
                                name='rolle' if settings.OS == 'Linux' else "Rolle",
                                create_type=False), nullable=False)
    telefonnummer = Column(String)
    adresse_id = Column(Integer, ForeignKey(f'Adresse.adresse_id' if settings.OS == 'Linux' else "Adresse.adresse_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Netzbetreiber(Base):
    __tablename__ = 'netzbetreiber' if settings.OS == 'Linux' else "Netzbetreiber"
    user_id = Column(Integer, Identity(), primary_key=True)


class Tarif(Base):
    __tablename__ = 'tarif' if settings.OS == 'Linux' else "Tarif"
    tarif_id = Column(Integer, Identity(), primary_key=True)
    tarifname = Column(String, unique=True)
    preis_kwh = Column(Float)
    grundgebuehr = Column(Float)
    laufzeit = Column(Integer)
    spezielle_konditionen = Column(String)


class Preisstrukturen(Base):
    __tablename__ = 'preisstrukturen' if settings.OS == 'Linux' else "Preisstrukturen"
    preis_id = Column(Integer, Identity(), primary_key=True)
    bezugspreis_kwh = Column(Float)
    einspeisung_kwh = Column(Float)


class DashboardSmartMeterData(Base):
    __tablename__ = "dashboard_smartmeter_data" if settings.OS == 'Linux' else "Dashboard_smartmeter_data"


    id = Column(Integer, primary_key=True, index=True)
    haushalt_id = Column(Integer, ForeignKey('Nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    datum = Column(DateTime)
    pv_erzeugung = Column(Float)
    soc = Column(Float)
    batterie_leistung = Column(Float)
    zaehler = Column(Float)
    last = Column(Float)

class Energieberatende(Base):
    __tablename__ = 'energieberatende' if settings.OS == 'Linux' else "Energieberatende"
    user_id = Column(Integer, ForeignKey('Nutzer.user_id'), primary_key=True)
    spezialisierung = Column(String)

class Solarteur(Base):
    __tablename__ = 'solarteur' if settings.OS == 'Linux' else "Solarteur"
    user_id = Column(Integer, ForeignKey('Nutzer.user_id'), primary_key=True)

class Haushalt(Base):
    __tablename__ = 'haushalt' if settings.OS == 'Linux' else "Haushalt"
    user_id = Column(Integer, ForeignKey('Nutzer.user_id'), primary_key=True)
    anzahl_bewohner = Column(Integer)
    heizungsart = Column(String)
    baujahr = Column(Integer)
    wohnflaeche = Column(Float)
    isolierungsqualitaet = Column(Enum(Isolierungsqualitaet)) 
    ausrichtung_dach = Column(Enum(AusrichtungDach))  
    dachflaeche = Column(Float)
    energieeffizienzklasse = Column(String)

class Rechnung(Base):
    __tablename__ = 'rechnungen' if settings.OS == 'Linux' else "Rechnungen"
    rechnung_id = Column(Integer, primary_key=True)
    haushalt_id = Column(Integer, ForeignKey('Haushalt.user_id'))
    rechnungsbetrag = Column(Float)
    rechnungsdatum = Column(Date)
    faelligkeitsdatum = Column(Date)
    rechnungsart = Column(Enum(Rechnungsart), nullable=False)
    zeitraum = Column(Date)

class Vertrag(Base):
    __tablename__ = 'vertrag' if settings.OS == 'Linux' else "Vertrag"
    vertrag_id = Column(String, primary_key=True)
    haushalt_id = Column(Integer, ForeignKey('Haushalt.user_id'))
    tarif_id = Column(Integer, ForeignKey('Tarif.tarif_id'))
    beginn_datum = Column(Date)
    end_datum = Column(Date)
    jahresabschlag = Column(Float)
    vertragstatus = Column(Boolean, default=True) 
