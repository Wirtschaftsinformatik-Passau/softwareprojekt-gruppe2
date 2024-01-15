import {Nutzerrolle} from "./user";

export interface ISearchItem {
    label: string;
    link: string;
}

export interface ISearchBarItems {
    [key: string]: ISearchItem[];
}

export const searchBarItems: ISearchBarItems = {
    Admin: [
        { label: "Dashboard", link: "/admin/" },
        { label: "Nutzer", link: "/admin/userTable" },
        { label: "Nutzer bearbeiten", link: "/admin/editUser" },
        { label: "Nutzer anlegen", link: "/admin/userCreation" },
        { label: "Kalender", link: "/admin/calendar" },
        { label: "FAQ", link: "/admin/faq" },
        { label: "Logs", link: "/admin/logOverview" },
        { label: "Endpunktaktivität", link: "/admin/endpointActivity" },
        { label: "Rollenübersicht", link: "/admin/roleOverview" },
    ],
    Netzbetreiber: [
        { label: "Dashboard", link: "/netzbetreiber/dashboard" },
        { label: "Tarife", link: "/netzbetreiber/tarifTable" },
        { label: "Tarif erstellen", link: "/netzbetreiber/tarifCreate" },
        { label: "Tarif bearbeiten", link: "/netzbetreiber/tarifEdit" },
        { label: "Kalender", link: "/netzbetreiber/calendar" },
        { label: "FAQ", link: "/netzbetreiber/faq" },
        { label: "Kündigungsanfragen", link: "/netzbetreiber/vertraegeKuendigung" },
        { label: "Verträge", link: "/netzbetreiber/vertraege" },
        { label: "Preise", link: "/netzbetreiber/priceTable" },
        { label: "Preis erstellen", link: "/netzbetreiber/priceCreate" },
        { label: "Preis bearbeiten", link: "/netzbetreiber/priceEdit" },
        { label: "Smart Meter Upload", link: "/netzbetreiber/smartmeterUpload" },
        { label: "Smart Meter Übersicht", link: "/netzbetreiber/smartmeterOverview" },
        {label: "Haushalte", link: "/netzbetreiber/haushalte"},
        {label: "Einspeisungsanträge", link: "/netzbetreiber/einspeisungen"},
        {label: "Angenommen Einspeisungsanträge", link: "/netzbetreiber/einspeisungenAngenommen"},

    ],
};