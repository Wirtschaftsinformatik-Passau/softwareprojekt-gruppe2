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
import EnergieberatendeAnfragenBearbeitet from "../../components/energieberatende/dashboard/EnergieberatendeAnfragenBearbeitet";
import EnergieberatendeAnfragenAbgeschlossen from "../../components/energieberatende/dashboard/EnergieberatendeAnfragenAbgeschlossen";
import EnergieberatendeAnfragenDetail from "../../components/energieberatende/dashboard/EnergieberatendeAnfragenDetail";
import EnergieberaterRechnungsTable from "../../components/energieberatende/dashboard/EnergieberatendeRechnungenOverview";
import Calendar from "../../components/all/dashboards/Calendar";

const  EnergieberatendeDashboard = () => {

    const [theme, colorMode] = useMode();
    const faqItems = [
        {
            title: "What is GreenEcoHub?",
            text: "GreenEcoHub is a platform that allows users to track their carbon footprint and compare it to other users. It also allows users to track their progress in reducing their carbon footprint and provides tips on how to reduce it further.",
        }, {
            title: "How do I use GreenEcoHub?",
            text: "To use GreenEcoHub, you must first create an account. Once you have created an account, you can log in and begin tracking your carbon footprint. You can also view your progress and compare it to other users.",
        }
    ]
    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-100" style={{marginTop: "64px"}}>
                <EnergieSidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true}/>
                <Routes>
                <Route path="/antragTable/:anlageID" element={<EnergieberatendeAnfragenDetail/>}/>
                <Route path="/antragTableAbgeschlossen" element={<EnergieberatendeAnfragenAbgeschlossen/>}/>
                <Route path="/antragTableBearbeitet" element={<EnergieberatendeAnfragenBearbeitet/>}/>
                <Route path="/antragTable" element={<EnergieberatendeAnfragen/>}/>
                <Route path="/rechnungenOverview" element={<EnergieberaterRechnungsTable/>}/>
                <Route path="/calendar" element={<Calendar/>}/>
                <Route path="/faq" element={<FAQ faqItems={faqItems}/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default EnergieberatendeDashboard;