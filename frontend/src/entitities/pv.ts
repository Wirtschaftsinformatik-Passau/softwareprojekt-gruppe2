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




export interface EnergieausweisCreate {
    energieeffizienzklasse: string | "",
    verbrauchskennwerte: number | "",
    gueltigkeit: number | "",
}