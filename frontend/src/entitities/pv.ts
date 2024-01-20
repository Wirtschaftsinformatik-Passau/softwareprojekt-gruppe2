import { en } from "@fullcalendar/core/internal-common"
import { Orientierung } from "./haushalt"

export interface PVAntrag {
    anlage_id: number | "",
    haushalt_id: number | "",
    solarteur_id: number | "",
    prozess_status: ProzessStatus | "",
    nvpruefung_status: boolean | "Noch nicht geprüft",
}

export interface Angebot {
    angebot_id: number ,
    modulanordnung: Orientierung | "",
    modultyp: string | "",
    kapazitaet: number | "",
    installationsflaeche: number | "",
    kosten: number | "",
    angebotsstatus: boolean | "",
    created_at: Date | "",
    
}



export enum Montagesystem {
    Aufdachmontage = "Aufdachmontage",
    Indachmontage = "Indachmontage",
    Flachdachmontage = "Flachdachmontage",
    Freilandmontage = "Freilandmontage",
    Trackermontage = "Trackermontage",
    Fassadenmontage = "Fassadenmontage"
}


export enum Schatten {
    Kein_Schatten = "Kein_Schatten",
    Minimalschatten = "Minimalschatten",
    Moderater_Schatten = "Moderater_Schatten",
    Ausgedehnter_Schatten = "Ausgedehnter_Schatten",
    Dauerhafter_Schatten = "Dauerhafter_Schatten"
}

export interface Installationsplan {
    kabelwegfuehrung: string | "",
    montagesystem: Montagesystem | "",
    schattenanalyse: Schatten | "",
    wechselrichterposition: string | "",
    installationsdatum: Date | "",
}

export enum ProzessStatus {
    AnfrageGestellt = 'AnfrageGestellt',
    DatenAngefordert = 'DatenAngefordert',
    DatenFreigegeben = 'DatenFreigegeben',
    AngebotGemacht = 'AngebotGemacht',
    AngebotAngenommen = 'AngebotAngenommen',
    AusweisErstellt = 'AusweisErstellt',
    AusweisAngefordert = 'AusweisAngefordert',
    PlanErstellt = 'PlanErstellt',
    Genehmigt = "Genehmigt",
    Abgenommen = 'Abgenommen',
    InstallationAbgeschlossen = 'InstallationAbgeschlossen'
}

export interface PVAngebotCreate{
    anlage_id: number | "",
    modultyp: string | "",
    kapazitaet: number | "",
    installationsflaeche: number | "",
    modulanordnung: Orientierung | "",
    kosten: number | "",
}

export interface SolarteurResponse {
    anlage_id: number,
    vorname: string,
    nachname: string,
    email: string,
    strasse: string,
    hausnummer: number,
    plz: number,    
    stadt: string,
    prozess_status: string,

}


export interface EnergieberaterResponseFinal extends SolarteurResponse{
    solarteur_id: Number,
    modultyp: String,
    kapazitaet: Number, 
    installationsflaeche: Number,
    installationsdatum: Date,
    installationsstatus: String,
    modulanordnung: String,
    kabelwegfuehrung: String,
    montagesystem: String
    schattenanalyse: String,
    wechselrichterposition: String,
    installationsplan: String,
    energieausweis_id: Number
}

export interface NetzbetreiberPVResponse extends SolarteurResponse{
    
}

export interface EnergieausweisCreate {
    energieeffizienzklasse: string | "",
    verbrauchskennwerte: number | "",
    gueltigkeit: number | "",
}

export interface EnergieeffizienzmassnahmenCreate {
    massnahmetyp: MassnahmeTyp | "",
    einsparpotenzial: number | "",
    kosten: number | "",
}

export enum MassnahmeTyp {
    Isolierung = "Isolierung",
    Heizungssystem = "Heizungssystem",
    Fenstererneuerung = "Fenstererneuerung"
}

export interface NetzbetreiberDetailPV {
    anlage_id: number | "";
    haushalt_id: number | "";
    solarteur_id: number | "";
    modultyp: string | "";
    kapazitaet: number | "";
    installationsflaeche: number | "";
    installationsdatum: Date | "";
    modulanordnung: Orientierung | "";
    kabelwegfuehrung: string | "";
    montagesystem: Montagesystem | "";
    schattenanalyse: boolean | "";
    wechselrichterposition: string | "";
    installationsplan: string | "";
    prozess_status: ProzessStatus | "";
    nvpruefung_status: string | "";
    vorname: string | "";
    nachname: string | "",
    strasse: string | "",
    hausnr: number | "",
    plz: number | "",
    stadt: string | ""

}



export enum Rechnungsart {
    Netzbetreiber_Rechnung = 'Netzbetreiber_Rechnung',
    Energieberater_Rechnung = 'Energieberater_Rechnung',
    Solarteur_Rechnung = 'Solarteur_Rechnung'

}

export interface Rechnung {
    rechnung_id: number | "",
    empfaenger_id: number | "",
    steller_id: number | "",
    rechnungsbetrag: number | "",
    rechnungsdatum: Date | "",
    faelligkeitsdatum: Date | "",
    rechnungsart: Rechnungsart | "",

}

export enum Zahlungsstatus {
    Bezahlt = "Bezahlt",
    Offen = "Offen",
    Teilweise_Bezahlt = "Teilweise_Bezahlt",
    Storniert = "Storniert",
    Überfällig = "Überfällig"
}