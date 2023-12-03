import enum
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Enum, ForeignKey, UUID, \
    Identity
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, date


class Rolle(enum.Enum):
    Haushalte = 'Haushalte'
    Solarteure = 'Solarteure'
    Energieberatende = 'Energieberatende'
    Netzbetreiber = 'Netzbetreiber'
    Admin = 'Admin'


class Adresse(Base):
    __tablename__ = 'adresse'

    adresse_id = Column(Integer, Identity(), primary_key=True)
    strasse = Column(String)
    hausnummer = Column(Integer)
    zusatz = Column(String)
    plz = Column(Integer)
    stadt = Column(String)
    land = Column(String)


class Nutzer(Base):
    __tablename__ = 'nutzer'
    user_id = Column(Integer, Identity(), primary_key=True)
    nachname = Column(String)
    vorname = Column(String)
    geburtsdatum = Column(Date)
    email = Column(String)
    passwort = Column(String)
    rolle = Column(Enum(Rolle))
    telefonnummer = Column(String)
    adresse_id = Column(Integer, ForeignKey('adresse.adresse_id'))

    logs = relationship("Log", back_populates="user")


class Netzbetreiber(Base):
    __tablename__ = 'netzbetreiber'
    user_id = Column(Integer, Identity(), primary_key=True)


class AenderungsartEnum(enum.Enum):
    Informationsfreigabe = 'Informationsfreigabe'
    Vertragszugriff = 'Vertragszugriff'
    Rechnungszugriff = 'Rechnungszugriff'
    Vertragsaenderung = 'Vertragsaenderung'
    DokumentenDownload = 'DokumentenDownload'


class Log(Base):
    __tablename__ = 'logs'
    log_id = Column(Integer, Identity(), primary_key=True)
    zeitpunkt = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('nutzer.user_id'))
    aenderungsart = Column(Enum(AenderungsartEnum))

    user = relationship("Nutzer", back_populates="logs")


class Stromtarif(Base):
    __tablename__ = 'stromtarife'
    tarif_id = Column(Integer, Identity(), primary_key=True)
    tarifname = Column(String, unique=True)
    preis_pro_kwh = Column(Float)
    grundgebuehr = Column(Float)
    laufzeit = Column(Integer)


class Vertrag(Base):
    __tablename__ = 'vertraege'
    vertrag_id = Column(Integer, Identity(), primary_key=True)
    haushalt_id = Column(Integer, ForeignKey('nutzer.user_id'))
    tarif_id = Column(Integer, ForeignKey('stromtarife.tarif_id'))
    beginn_datum = Column(Date)
    end_datum = Column(Date)
    jahresabschlag = Column(Float)
    vertragstatus = Column(Boolean)
