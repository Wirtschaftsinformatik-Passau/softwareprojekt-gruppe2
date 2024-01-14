
export interface Vertrag {
  "vorname": string,
  "nachname": string,
  "email": string,
  "vertrag_id": number,
  "netzbetreiber_id": number,
  "tarif_id": number,
  "beginn_datum": string,
  "end_datum": string,
  "jahresabschlag": number,
  "tarifname": string,
  "preis_kwh": number,
  "vertragstatus": Vertragsstatus | "",
  "grundgebuehr": number,
  "laufzeit": 0,
  "spezielle_konditionen": string,
}

export enum Vertragsstatus {
    Gekuendigt = "Gekuendigt",
    Laufend = "Laufend",
    Gekuendigt_Unbestaetigt = "Gekuendigt_Unbestaetigt"
}