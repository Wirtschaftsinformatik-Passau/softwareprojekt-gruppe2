import enum


class Rolle(enum.Enum):
    Haushalte = 'Haushalte'
    Solarteure = 'Solarteure'
    Energieberatende = 'Energieberatende'
    Netzbetreiber = 'Netzbetreiber'
    Admin = 'Admin'


class Isolierungsqualitaet(enum.Enum):
    hoch = 'hoch'
    mittel = 'mittel'
    niedrig = 'niedrig'


class Rechnungsart(enum.Enum):
    Netzbetreiber_Rechnung = 'Netzbetreiber_Rechnung'
    Energieberater_Rechnung = 'Energieberater_Rechnung'
    Solarteur_Rechnung = 'Solarteur_Rechnung'


class ProzessStatus(enum.Enum):
    AnfrageGestellt = 'AnfrageGestellt'
    DatenAngefordert = 'DatenAngefordert'
    DatenFreigegeben = 'DatenFreigegeben'
    AngebotGemacht = 'AngebotGemacht'
    AngebotAngenommen = 'AngebotAngenommen'
    AngebotAbgelehnt = 'AngebotAbgelehnt'
    AusweisAngefordert = 'AusweisAngefordert'
    AusweisErstellt = 'AusweisErstellt'
    PlanErstellt = 'PlanErstellt'
    Genehmigt = "Genehmigt"
    Abgenommen = 'Abgenommen'
    InstallationAbgeschlossen = 'InstallationAbgeschlossen'


class Montagesystem(enum.Enum):
    Aufdachmontage = "Aufdachmontage"
    Indachmontage = "Indachmontage"
    Flachdachmontage = "Flachdachmontage"
    Freilandmontage = "Freilandmontage"
    Trackermontage = "Trackermontage"
    Fassadenmontage = "Fassadenmontage"


class Orientierung(enum.Enum):
    Nord = "Nord"
    Nordost = "Nordost"
    Ost = "Ost"
    Suedost = "Suedost"
    Sued = "Sued"
    Suedwest = "Suedwest"
    West = "West"
    Nordwest = "Nordwest"


class Schatten(enum.Enum):
    Kein_Schatten = "Kein_Schatten"
    Minimalschatten = "Minimalschatten"
    Moderater_Schatten = "Moderater_Schatten"
    Ausgedehnter_Schatten = "Ausgedehnter_Schatten"
    Dauerhafter_Schatten = "Dauerhafter_Schatten"


class AusweisStatus(enum.Enum):
    AnfrageGestellt = "AnfrageGestellt"
    ZusatzdatenEingegeben = "ZusatzdatenEingegeben"
    Ausgestellt = "Ausgestellt"


class MassnahmeTyp(enum.Enum):
    Isolierung = "Isolierung"
    Heizungssystem = "Heizungssystem"
    Fenstererneuerung = "Fenstererneuerung"

class Vertragsstatus(enum.Enum):
    Gekuendigt = "Gekuendigt"
    Laufend = "Laufend"
    Gekuendigt_Unbestaetigt = "Gekuendigt_Unbestaetigt"


class Zahlungsstatus(enum.Enum):
    Bezahlt = "Bezahlt",
    Offen = "Offen",
    Teilweise_Bezahlt = "Teilweise_Bezahlt"
    Storniert = "Storniert"
    Ueberfaellig = "Ueberfaellig"
