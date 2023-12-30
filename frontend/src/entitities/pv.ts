export interface PVAntrag {
    anlage_id: number | "",
    haushalt_id: number | "",
    solarteur_id: number | "",
    prozess_status: ProzessStatus | "",
    nvpruefung_status: boolean | "Noch nicht geprüft",
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