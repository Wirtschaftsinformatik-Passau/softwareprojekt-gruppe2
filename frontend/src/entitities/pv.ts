export interface PVAntrag {
    anlage_id: number | "",
    haushalt_id: number | "",
    solarteur_id: number | "",
    prozess_status: ProzessStatus | "",
    nvpruefung_status: boolean | "Noch nicht geprüft",
}

export interface Angebot {
    angebot_id: number | "",
    kosten: number | "",
    angebotsstatus: boolean | "",
    created_at: Date | "",
}

enum ProzessStatus {
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