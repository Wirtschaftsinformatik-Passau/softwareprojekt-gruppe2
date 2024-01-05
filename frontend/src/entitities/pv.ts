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
    kosten: number | "",
    angebotsstatus: boolean | "",
    created_at: Date | "",
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