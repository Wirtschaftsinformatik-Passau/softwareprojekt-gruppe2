from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Enum, ForeignKey, \
    Identity, TIMESTAMP, func, UniqueConstraint, Numeric
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.config import settings
from app.types import (Rolle, Orientierung, ProzessStatus, Montagesystem, Schatten, AusweisStatus,
                       Isolierungsqualitaet, Rechnungsart, MassnahmeTyp, Vertragsstatus, Zahlungsstatus)



class Adresse(Base):
    __tablename__ = 'adresse' if settings.OS == 'Linux' else "Adresse"

    adresse_id = Column(Integer, Identity(), primary_key=True)
    strasse = Column(String)
    hausnummer = Column(Integer)
    zusatz = Column(String)
    plz = Column(Integer)
    stadt = Column(String)
    land = Column(String)
    longitude = Column(Float)
    latitude = Column(Float)


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
    adresse_id = Column(Integer, ForeignKey(f'adresse.adresse_id' if settings.OS == 'Linux' else "Adresse.adresse_id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())



class Netzbetreiber(Base):
    __tablename__ = 'netzbetreiber' if settings.OS == 'Linux' else "Netzbetreiber"
    user_id = Column(Integer, Identity(), primary_key=True)
    arbeitgeber = Column(Boolean, default=False)


class Tarif(Base):
    __tablename__ = 'tarif' if settings.OS == 'Linux' else "Tarif"
    tarif_id = Column(Integer, Identity(), primary_key=True)
    tarifname = Column(String, unique=True)
    preis_kwh = Column(Float)
    grundgebuehr = Column(Float)
    laufzeit = Column(Integer)
    spezielle_konditionen = Column(String)
    netzbetreiber_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Preisstrukturen(Base):
    __tablename__ = 'preisstrukturen' if settings.OS == 'Linux' else "Preisstrukturen"
    preis_id = Column(Integer, Identity(), primary_key=True)
    bezugspreis_kwh = Column(Float)
    einspeisung_kwh = Column(Float)
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())


class DashboardSmartMeterData(Base):
    __tablename__ = "dashboard_smartmeter_data" if settings.OS == 'Linux' else "Dashboard_smartmeter_data"

    id = Column(Integer, primary_key=True, index=True)
    haushalt_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    datum = Column(DateTime)
    pv_erzeugung = Column(Float)
    soc = Column(Float)
    batterie_leistung = Column(Float)
    zaehler = Column(Float)
    last = Column(Float)
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))


class PVAnlage(Base):
    __tablename__ = 'pvanlage' if settings.OS == 'Linux' else 'PVAnlage'
    anlage_id = Column(Integer, Identity(), primary_key=True)
    haushalt_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    solarteur_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    netzbetreiber_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"),
                              nullable=True)
    modultyp = Column(String, nullable=True)
    energieausweis_id = Column(Integer, ForeignKey(
        'energieausweise.energieausweis_id' if settings.OS == 'Linux' else "Energieausweise.energieausweis_id"))
    kapazitaet = Column(Float, nullable=True)
    installationsflaeche = Column(Float, nullable=True)
    installationsdatum = Column(Date, nullable=True)
    modulanordnung = Column(Enum(Orientierung), ENUM(*[r.value for r in Orientierung],
                                                     name='modulanordnung' if settings.OS == 'Linux' else "Modulanordnung",
                                                     create_type=False), nullable=True)
    kabelwegfuehrung = Column(String)
    montagesystem = Column(Enum(Montagesystem), ENUM(*[r.value for r in Montagesystem],
                                                     name='montagesystem' if settings.OS == 'Linux' else "Montagesystem",
                                                     create_type=False), nullable=True)
    schattenanalyse = Column(Enum(Schatten), ENUM(*[r.value for r in Schatten],
                                                  name='schattenanalyse' if settings.OS == 'Linux' else "Schattenanalyse",
                                                  create_type=False), nullable=True)
    wechselrichterposition = Column(String, nullable=True)
    installationsplan = Column(String)  # Verweis auf Dateipfad oder URL
    prozess_status = Column(Enum(ProzessStatus), ENUM(*[r.value for r in ProzessStatus],
                                                      name='prozessstatus' if settings.OS == 'Linux' else "ProzessStatus",
                                                      create_type=False), nullable=True)
    nvpruefung_status = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Angebot(Base):
    __tablename__ = "angebote" if settings.OS == 'Linux' else 'Angebote'

    angebot_id = Column(Integer, primary_key=True, index=True)
    anlage_id = Column(Integer, ForeignKey("pvanlage.anlage_id" if settings.OS == 'Linux' else "PVAnlage.anlage_id"))
    kosten = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Kalendereintrag(Base):
    __tablename__ = "kalendereintraege" if settings.OS == 'Linux' else 'Kalendereintraege'

    kalender_id = Column(Integer, Identity(), primary_key=True)
    start = Column(DateTime)
    ende = Column(DateTime)
    allDay = Column(Boolean)
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    beschreibung = Column(String)


class Energieausweise(Base):
    __tablename__ = 'energieausweise' if settings.OS == 'Linux' else 'Energieausweise'

    energieausweis_id = Column(Integer, primary_key=True)
    haushalt_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"),
                         nullable=False)
    massnahmen_id = Column(Integer, ForeignKey('energieeffizienzmassnahmen.massnahmen_id' if settings.OS == 'Linux'
                                               else "Energieeffizienzmassnahmen.massnahmen_id"), nullable=True)
    energieberater_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"),
                               nullable=True)
    energieeffizienzklasse = Column(String, nullable=True)
    verbrauchskennwerte = Column(Float, nullable=True)
    ausstellungsdatum = Column(Date, nullable=True)
    gueltigkeit = Column(Date, nullable=True)
    ausweis_status = Column(Enum(AusweisStatus), ENUM(*[r.value for r in Rolle],
                                                      name='ausweisstatus' if settings.OS == 'Linux' else "AusweisStatus",
                                                      create_type=False), nullable=False)


class Energieberatende(Base):
    __tablename__ = 'energieberatende' if settings.OS == 'Linux' else "Energieberatende"
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"),
                     primary_key=True)
    spezialisierung = Column(String)


class Solarteur(Base):
    __tablename__ = 'solarteur' if settings.OS == 'Linux' else "Solarteur"
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"),
                     primary_key=True)


class Haushalte(Base):
    __tablename__ = 'haushalte' if settings.OS == 'Linux' else "Haushalte"
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"),
                     primary_key=True)
    anzahl_bewohner = Column(Integer, nullable=True)
    heizungsart = Column(String, nullable=True)
    baujahr = Column(Integer, nullable=True)
    wohnflaeche = Column(Float, nullable=True)
    isolierungsqualitaet = Column(Enum(Isolierungsqualitaet), ENUM(*[r.value for r in Isolierungsqualitaet],
                                                                   name='isolierungsqualitaet' if settings.OS == 'Linux' else "Isolierungsqualitaet",
                                                                   create_type=False), nullable=True)
    ausrichtung_dach = Column(Enum(Orientierung), ENUM(*[r.value for r in Orientierung],
                                                       name='orientierung' if settings.OS == 'Linux' else "Orientierung",
                                                       create_type=False), nullable=True)
    dachflaeche = Column(Float, nullable=True)
    energieeffizienzklasse = Column(String, nullable=True)
    anfragestatus = Column(Boolean, nullable=True)


class Rechnungen(Base):
    __tablename__ = 'rechnungen' if settings.OS == 'Linux' else 'Rechnungen'
    rechnung_id = Column(Integer, primary_key=True)
    empfaenger_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    rechnungsbetrag = Column(Numeric(precision=11, scale=2))
    rechnungsdatum = Column(Date)
    faelligkeitsdatum = Column(Date)
    rechnungsart = Column(Enum(Rechnungsart), ENUM(*[r.value for r in Rechnungsart],
                                                   name='rechnungsart' if settings.OS == 'Linux' else "Rechnungsart",
                                                   create_type=False))
    steller_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    zahlungsstatus = Column(Enum(Zahlungsstatus), ENUM(*[r.value for r in Zahlungsstatus],
                                                       name='zahlungsstatus' if settings.OS == 'Linux'
                                                       else "Zahlungsstatus", create_type=False))
    rechnungsperiode_start = Column(Date)
    rechnungsperiode_ende = Column(Date)



class Vertrag(Base):
    __tablename__ = 'vertrag' if settings.OS == 'Linux' else "Vertrag"
    vertrag_id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    tarif_id = Column(Integer, ForeignKey('tarif.tarif_id' if settings.OS == 'Linux' else 'Tarif.tarif_id'))
    beginn_datum = Column(Date)
    end_datum = Column(Date)
    netzbetreiber_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    jahresabschlag = Column(Float)
    vertragstatus = Column(Enum(Vertragsstatus),
                           default=Vertragsstatus.Laufend.value,  # default-Wert
                           name='vertragsstatus' if settings.OS == 'Linux' else "Vertragsstatus")
    __table_args__ = (
        UniqueConstraint('user_id', 'tarif_id', name='_user_id_tarif_id_uc'),
    )


class Energieeffizienzmassnahmen(Base):
    __tablename__ = 'energieeffizienzmassnahmen' if settings.OS == 'Linux' else "Energieeffizienzmassnahmen"
    massnahmen_id = Column(Integer, primary_key=True)
    haushalt_id = Column(Integer, ForeignKey('nutzer.user_id'
                                             if settings.OS == 'Linux' else "Nutzer.user_id"))
    massnahmetyp = Column(Enum(MassnahmeTyp), ENUM(*[r.value for r in MassnahmeTyp],
                                                   name='massnahmetyp' if settings.OS == 'Linux' else "Massnahmetyp",
                                                   create_type=False))
    einsparpotenzial = Column(Float)
    kosten = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Kündigungsanfrage(Base):
    __tablename__ = 'kündigungsanfrage' if settings.OS == 'Linux' else "Kündigungsanfrage"
    anfrage_id = Column(Integer, primary_key=True)
    vertrag_id = Column(Integer, ForeignKey('vertrag.vertrag_id' if settings.OS == 'Linux' else 'Vertrag.vertrag_id'))
    bestätigt = Column(Boolean, default=False)
    neuer_tarif_id = Column(Integer, ForeignKey('tarif.tarif_id' if settings.OS == 'Linux' else 'Tarif.tarif_id'))


class Arbeitsverhältnis(Base):
    __tablename__ = 'arbeitsverhältnis' if settings.OS == 'Linux' else "Arbeitsverhältnis"
    arbeitsverhältnis_id = Column(Integer, primary_key=True)
    arbeitgeber_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    arbeitnehmer_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))


class PasswortResetToken(Base):
    __tablename__ = 'passwort_reset_tokens' if settings.OS == 'Linux' else "Passwort_reset_tokens"
    token_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    token = Column(String, unique=True, index=True)
    expiration = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = 'chat_messages' if settings.OS == 'Linux' else "Chat_messages"
    nachricht_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    empfaenger_id = Column(Integer, ForeignKey('nutzer.user_id' if settings.OS == 'Linux' else "Nutzer.user_id"))
    nachricht_inhalt = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())

