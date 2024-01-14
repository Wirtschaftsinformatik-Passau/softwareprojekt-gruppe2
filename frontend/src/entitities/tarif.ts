export interface ITarif {
    tarifname: string,
    preis_kwh: number,
    grundgebuehr: number,
    laufzeit: number,
    spezielle_konditionen: string,
}

export class Tarif implements ITarif{
    public tarifname;
    public preis_kwh;
    public grundgebuehr;
    public laufzeit;
    public spezielle_konditionen;

    constructor(
        tarifName: string,
        preisKwh: number,
        grundgebuehr: number,
        laufzeit: number,
        spezielleKonditionen: string
    ) {
        this.tarifname = tarifName;
        this.preis_kwh = preisKwh
        this.grundgebuehr = grundgebuehr
        this.laufzeit = laufzeit
        this.spezielle_konditionen = spezielleKonditionen
    }
}

