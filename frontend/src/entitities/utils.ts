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
    Solarteure: [
        { label: "Dashboard", link: "/solarteure/" },
        { label: "Kalender", link: "/solarteure/calendar" },
        { label: "FAQ", link: "/solarteure/faq" },
        { label: "Offene Anträge", link: "/solarteure/antragTable" },
        { label: "Bearbeitete Anträge", link: "/solarteure/antragTableBearbeitet" },
        { label: "Abgeschlossene Anträge", link: "/solarteure/antragTableAbgeschlossen" },
        { label: "Rechnungen", link: "/solarteure/rechnungenOverview" },
        { label: "Chat", link: "/solarteure/chat" },
    ],
    Haushalte: [
        { label: "Dashboard", link: "/haushalte/" },
        { label: "Kalender", link: "/haushalte/calendar" },
        { label: "FAQ", link: "/haushalte/faq" },
        { label: "Verträge", link: "/haushalte/vertragOverview" },
        { label: "Tarifübersicht", link: "/haushalte/tarifTable" },
        { label: "Chat", link: "/haushalte/chat" },
        { label: "Haushaltsdaten", link: "/haushalte/dataOverview" },
        { label: "Rechnungen", link: "/haushalte/rechnungenOverview" },
        { label: "Einspeisungsanfrage stellen", link: "/haushalte/einspeisungsanfrage" },
        { label: "Einspeisungsantrag", link: "/haushalte/einspeisungsantrag" },
        { label: "Übersicht über gestellte Anträge", link: "/haushalte/eispesungsantragOverview" },
        { label: "Smartmeter Daten Upload", link: "/haushalte/pvuploadOverview" },
        { label: "Smartmeter Daten Übersicht", link: "/haushalte/smartMeterOverview" },
        { label: "Rechnungen", link: "/haushalte/rechnungenOverview" },
    ],
    Energieberantende: [
        { label: "Dashboard", link: "/energieberatende/" },
        { label: "Kalender", link: "/energieberatende/calendar" },
        { label: "FAQ", link: "/energieberatende/faq" },
        { label: "Chat", link: "/energieberatende/chat" },
        { label: "Offene Anträge", link: "/energieberatende/antragTable" },
        { label: "Bearbeitete Anträge", link: "/energieberatende/antragTableBearbeitet" },
        { label: "Abgeschlossene Anträge", link: "/energieberatende/antragTableAbgeschlossen" },
        { label: "Rechnungen", link: "/energieberatende/rechnungenOverview" },
    ],
};