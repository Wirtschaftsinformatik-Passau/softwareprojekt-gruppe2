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

class AusrichtungDach(enum.Enum):
    Nord = 'Nord'
    Nordost = 'Nordost'
    Ost = 'Ost'
    Suedost = 'Suedost'
    Sued = 'Sued'
    Suedwest = 'Suedwest'
    West = 'West'
    Nordwest = 'Nordwest'

class Rechnungsart(enum.Enum):
    Netzbetreiber_Rechnung = 'Netzbetreiber_Rechnung'
    Energieberater_Rechnung = 'Energieberater_Rechnung'
    Solarteur_Rechnung = 'Solarteur_Rechnung'