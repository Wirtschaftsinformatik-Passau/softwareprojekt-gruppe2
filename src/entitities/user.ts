export interface IUser {
    titel?: string
    vorname: string
    nachname: string
    telefon: string
    email: string
    password: string
    role:  Nutzerrolle,
    geburtstag: Date
}

export enum Nutzerrolle {
    Admin,
    Netzbetreiber,
    Kunde,
    Berater
}



export class User implements IUser{
    public vorname;
    public nachname;
    public telefon;
    public titel;
    public email;
    public role;
    public geburtstag;
    public password: string;

    constructor(
        vorname: string,
        nachname: string,
        telefon: string,
        email: string,
        password: string,
        role:  Nutzerrolle,
        geburtstag: Date,
        title: string = ""
    ) {
        this.vorname = vorname;
        this.nachname = nachname
        this.telefon = telefon
        this.email = email
        this.password = password
        this.role = role
        this.geburtstag = geburtstag
        this.titel = title
    }
}

export interface UserDropDownOption {
    label: string
    value: Nutzerrolle
}

