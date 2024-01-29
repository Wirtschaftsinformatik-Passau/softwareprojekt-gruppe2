// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";
import Topbar from "../../components/all/Topbar"
import FAQ from "../../components/admin/dashboards/FAQs";
import EnergieSidebar from "../../components/energieberatende/dashboard/EnergieSidebar";
import EnergieberatendeAnfragen from "../../components/energieberatende/dashboard/EnergieberatendeAnfragen";
import EnergieHome from "../../components/energieberatende/dashboard/EnergieberatendeHome";
import EnergieberatendeAnfragenBearbeitet from "../../components/energieberatende/dashboard/EnergieberatendeAnfragenBearbeitet";
import EnergieberatendeAnfragenAbgeschlossen from "../../components/energieberatende/dashboard/EnergieberatendeAnfragenAbgeschlossen";
import EnergieberatendeAnfragenDetail from "../../components/energieberatende/dashboard/EnergieberatendeAnfragenDetail";
import EnergieberaterRechnungsTable from "../../components/energieberatende/dashboard/EnergieberatendeRechnungenOverview";
import Calendar from "../../components/all/dashboards/Calendar";

const  EnergieberatendeDashboard = () => {

    const [theme, colorMode] = useMode();
    const faqItems = [
        {
            title: "Wie verwalte ich Stromtarife und passe sie an Marktbedingungen an?",
            text: "Sie können über das Netzbetreiber-Dashboard Stromtarife erstellen, anpassen und verwalten, um sie an die aktuellen Marktbedingungen und Kundenbedürfnisse anzupassen."
        },
        {
            title: "Wie erstelle und verwalte ich Verträge und Rechnungen für Haushalte?",
            text: "Verträge und Rechnungen können durch die Nutzung spezialisierter Funktionen im System erstellt und verwaltet werden. Dazu gehören die Eingabe von Verbrauchsdaten und die Anwendung der entsprechenden Tarife."
        },
        {
            title: "Was beinhaltet die Verwaltung von Dashboards auf der Plattform?",
            text: "Die Dashboard-Verwaltung beinhaltet die Pflege und Aktualisierung von Ansichten und Daten, die eine Übersicht über den Energieverbrauch und die Energieerzeugung bieten."
        },
        {
            title: "Wie kann ich detaillierte Berichte über Energieverbrauch und -erzeugung exportieren?",
            text: "Sie können Berichte über das Dashboard exportieren, indem Sie Metriken und Zeiträume auswählen und das gewünschte Format für den Export bestimmen."
        },
        {
            title: "Welche Formate stehen für den Export von Berichten zur Verfügung?",
            text: "Berichte können in verschiedenen Formaten wie PDF, Excel oder CSV exportiert werden, um eine flexible Datenanalyse zu ermöglichen."
        },
        {
            title: "Wie kann ich Einspeisezusagen für Photovoltaikanlagen erteilen?",
            text: "Einspeisezusagen werden erteilt, indem Sie Anträge auf Einspeisung überprüfen und auf Basis der Netzkapazitäten und geplanten Einspeisungen entscheiden."
        },
        {
            title: "Wie überprüfe ich Anträge auf Einspeisung?",
            text: "Anträge werden im System überprüft, wobei technische und kapazitive Aspekte des Stromnetzes berücksichtigt werden."
        },
        {
            title: "Wie treffe ich Entscheidungen bezüglich Einspeisungen basierend auf Netzkapazitäten?",
            text: "Entscheidungen werden auf Grundlage der aktuellen und prognostizierten Netzkapazitäten sowie der Gesamteinspeisung getroffen."
        },
        {
            title: "Wie berechne und erstelle ich Rechnungen für Haushalte?",
            text: "Rechnungen werden basierend auf dem Energieverbrauch und den geltenden Tarifen berechnet und können direkt über das System erstellt werden."
        },
        {
            title: "Wie kann ich die Energieverbrauchsdaten effektiv nutzen?",
            text: "Die Daten können für die Tarifgestaltung, Verbrauchsanalyse und Optimierung der Netzauslastung genutzt werden."
        },
        {
            title: "Welche Funktionen stehen mir im Hinblick auf die Datenanalyse zur Verfügung?",
            text: "Sie haben Zugriff auf umfangreiche Analysetools, die es ermöglichen, Verbrauchs- und Erzeugungsdaten detailliert zu analysieren."
        },
        {
            title: "Wie kann ich die Daten für Energieberater und Solarteure zugänglich machen?",
            text: "Daten können über das System freigegeben oder in Form von Berichten zur Verfügung gestellt werden."
        },
        {
            title: "Wie kann ich die Plattform nutzen, um meine Verwaltungsaufgaben zu erleichtern?",
            text: "Die Plattform bietet verschiedene Werkzeuge zur Automatisierung und Vereinfachung von Verwaltungsaufgaben, wie Tarifverwaltung und Rechnungserstellung."
        },
        {
            title: "Welche Möglichkeiten habe ich zur Anpassung der Berichtsmetriken und -perioden?",
            text: "Sie können individuelle Berichtsmetriken und -perioden im System festlegen, um maßgeschneiderte Berichte zu erstellen."
        },
        {
            title: "Wie kann ich sicherstellen, dass die bereitgestellten Daten aktuell und genau sind?",
            text: "Durch regelmäßige Überprüfung und Aktualisierung der Daten im System können Sie deren Aktualität und Genauigkeit sicherstellen."
        }
    ]
    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-100" style={{marginTop: "64px"}}>
                <EnergieSidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true} nutzerrolle={"Energieberatende"}/>
                <Routes>
                <Route path="/" element={<EnergieHome/>}/>
                <Route path="/antragTable/:anlageID" element={<EnergieberatendeAnfragenDetail/>}/>
                <Route path="/antragTableAbgeschlossen" element={<EnergieberatendeAnfragenAbgeschlossen/>}/>
                <Route path="/antragTableBearbeitet" element={<EnergieberatendeAnfragenBearbeitet/>}/>
                <Route path="/antragTable" element={<EnergieberatendeAnfragen/>}/>
                <Route path="/rechnungenOverview" element={<EnergieberaterRechnungsTable/>}/>
                <Route path="/calendar" element={<Calendar/>}/>
                <Route path="/faq" element={<FAQ items={faqItems}/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default EnergieberatendeDashboard;