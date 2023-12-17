export interface IUser {
    titel?: string
    vorname: string
    nachname: string
    telefonnummer: string
    email: string
    passwort: string
    rolle:  string,
    geburtsdatum: string
    adresse_id: number
}

export interface ILoginUser {
    email: string
    passwort: string
}

export enum Nutzerrolle {
    Admin = "Admin",
    Netzbetreiber = "Netzbetreiber",
    Solarteure = "Solarteure",
    Energieberatende = "Energieberatende",
    Haushalte = "Haushalte"
}

export class LoginUser implements ILoginUser{
    public email;
    public passwort;

    constructor(
        email: string,
        password: string,
    ) {
        this.email = email;
        this.passwort = password
    }
}


export class User implements IUser{
    public vorname;
    public nachname;
    public telefonnummer;
    public titel;
    public email;
    public rolle;
    public geburtsdatum;
    public passwort;
    public adresse_id;

    constructor(
        vorname: string,
        nachname: string,
        telefon: string,
        email: string,
        passwort: string,
        rolle:  string,
        geburtsdatum: string,
        adresse_id: number,
        title: string = ""
    ) {
        this.vorname = vorname;
        this.nachname = nachname
        this.telefonnummer = telefon
        this.email = email
        this.passwort = passwort
        this.rolle = rolle
        this.geburtsdatum = geburtsdatum
        this.adresse_id = adresse_id
        this.titel = title
    }
}

export interface UserDropDownOption {
    label: string
    value: Nutzerrolle
}

