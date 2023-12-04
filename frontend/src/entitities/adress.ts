export interface Iadresse {
    strasse: string
    hausnummer: number
    zusatz?: string
    plz: number
    stadt: string
    land: string
}

export class Adresse implements Iadresse{
    public strasse;
    public hausnummer;
    public zusatz;
    public plz;
    public stadt;
    public land;

    constructor(
        strasse: string,
        hausnummer: number,
        plz: number,
        stadt: string,
        land: string,
        zusatz: string = ""
    ) {
        this.strasse = strasse;
        this.hausnummer = hausnummer
        this.plz = plz
        this.stadt = stadt
        this.land = land
        this.zusatz = zusatz
    }
}