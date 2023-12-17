import enum


class Rolle(enum.Enum):
    Haushalte = 'Haushalte'
    Solarteure = 'Solarteure'
    Energieberatende = 'Energieberatende'
    Netzbetreiber = 'Netzbetreiber'
    Admin = 'Admin'


class ProzessStatus(enum.Enum):
    AnfrageGestellt = 'AnfrageGestellt'
    AngebotGemacht = 'AngebotGemacht'
    AngebotAngenommen = 'AngebotAngenommen'
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
