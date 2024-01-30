// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";
import Topbar from "../../components/all/Topbar"
import Sidebar from "../../components/solarteure/dashboard/SolarteureSidebar";
import FAQ from "../../components/admin/dashboards/FAQs";
import SolarteureAnfragen from "../../components/solarteure/dashboard/SolarteureAnfragen";
import SolarteureAnfragenDetail from "../../components/solarteure/dashboard/SolarteureAnfragenDetail";
import SolarteuereAnfragenAbgeschlossen from "../../components/solarteure/dashboard/SolarteureAnfragenAbgeschlossen";
import SolarteureAnfragenBearbeitet from "../../components/solarteure/dashboard/SolarteureAnfragenBearbeitet";
import EnergieberaterRechnungsTable from "../../components/energieberatende/dashboard/EnergieberatendeRechnungenOverview";
import SolarteurHome from "../../components/solarteure/dashboard/SolarteureHome";
import Calendar from "../../components/all/dashboards/Calendar";
import { standardFAQ } from "../../utils/faqs";
import Chat from "../../components/all/Chat";


const  NetzbetreiberDashboard = () => {
    const [effect, setEffect] = useState("")
    const [theme, colorMode] = useMode();
    
    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-100" style={{marginTop: "64px"}}>
                <Sidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true} nutzerrolle={"Solarteure"}/>
                <Routes>
                    <Route path="/" element={<SolarteurHome/>}/>
                    <Route path="/antragTable" element={<SolarteureAnfragen/>}/>
                    <Route path="/antragTable/:anlageID" element={<SolarteureAnfragenDetail/>}/>
                    <Route path="/antragTableAbgeschlossen" element={<SolarteuereAnfragenAbgeschlossen/>}/>
                    <Route path="/antragTableBearbeitet" element={<SolarteureAnfragenBearbeitet/>}/>
                    <Route path="/rechnungenOverview" element={<EnergieberaterRechnungsTable/>}/>
                    <Route path="/calendar" element={<Calendar/>}/>
                    <Route path="/faq" element={<FAQ items={standardFAQ}/>}/>
                    <Route path="/chat" element={<Chat/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default NetzbetreiberDashboard;