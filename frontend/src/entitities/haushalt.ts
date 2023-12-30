
export enum Isolierungsqualitaet {
    hoch = 'hoch',
    mittel = 'mittel',
    niedrig = 'niedrig'
}


export enum Orientierung {
    Nord = "Nord",
    Nordost = "Nordost",
    Ost = "Ost",
    Suedost = "Suedost",
    Sued = "Sued",
    Suedwest = "Suedwest",
    West = "West",
    Nordwest = "Nordwest"
}


export interface IHaushaltData {
    anzahl_bewohner: number | "";
    heizungsart: string;
    baujahr: number | "";
    wohnflaeche: number | "";
    isolierungsqualitaet: Isolierungsqualitaet | "";
    ausrichtung_dach: Orientierung | "" ;
    dachflaeche: number | "";
    energieeffizienzklasse: string;
}
