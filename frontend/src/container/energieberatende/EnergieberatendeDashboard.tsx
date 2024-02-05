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
import Chat from "../../components/all/Chat";
import { standardFAQ } from "../../utils/faqs";

const  EnergieberatendeDashboard = () => {

    const [theme, colorMode] = useMode();

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-100" style={{marginTop: "64px"}}>
                <EnergieSidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true} nutzerrolle={"Energieberantende"}/>
                <Routes>
                <Route path="/" element={<EnergieHome/>}/>
                <Route path="/antragTable/:anlageID" element={<EnergieberatendeAnfragenDetail/>}/>
                <Route path="/antragTableAbgeschlossen" element={<EnergieberatendeAnfragenAbgeschlossen/>}/>
                <Route path="/antragTableBearbeitet" element={<EnergieberatendeAnfragenBearbeitet/>}/>
                <Route path="/chat" element={<Chat/>}/>
                <Route path="/antragTable" element={<EnergieberatendeAnfragen/>}/>
                <Route path="/rechnungenOverview" element={<EnergieberaterRechnungsTable/>}/>
                <Route path="/calendar" element={<Calendar/>}/>
                <Route path="/faq" element={<FAQ items={standardFAQ}/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default EnergieberatendeDashboard;