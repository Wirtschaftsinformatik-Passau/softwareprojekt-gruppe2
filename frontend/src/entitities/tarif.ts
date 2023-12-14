export interface ITarif {
    tarifName: string,
    preisKwh: number,
    grundgebuehr: number,
    laufzeit: number,
    spezielleKonditionen: string,
}

export class Tarif implements ITarif{
    public tarifName;
    public preisKwh;
    public grundgebuehr;
    public laufzeit;
    public spezielleKonditionen;

    constructor(
        tarifName: string,
        preisKwh: number,
        grundgebuehr: number,
        laufzeit: number,
        spezielleKonditionen: string
    ) {
        this.tarifName = tarifName;
        this.preisKwh = preisKwh
        this.grundgebuehr = grundgebuehr
        this.laufzeit = laufzeit
        this.spezielleKonditionen = spezielleKonditionen
    }
}