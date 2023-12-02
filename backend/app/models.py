from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Enum, ForeignKey, UUID, \
    Identity
from app.database import Base
from sqlalchemy.orm import relationship
import enum


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


class Netzbetreiber(Base):
    __tablename__ = 'netzbetreiber'
    user_id = Column(Integer, Identity(), primary_key=True)
