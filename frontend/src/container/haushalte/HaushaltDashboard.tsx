// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";
import Topbar from "../../components/all/Topbar"
import HaushalteSidebar from "../../components/haushalte/dashboard/HaushalteSidebar";
import HaushalteTarifTable from "../../components/haushalte/dashboard/HaushalteTarifTable";
import HaushalteVertragCreate from "../../components/haushalte/dashboard/HaushalteVertragCreate";
import HaushalteVertrag from "../../components/haushalte/dashboard/HaushaltVertrag";
import HaushalteVertragDetail from "../../components/haushalte/dashboard/HaushaltVertragDetail";
import HaushalteEinpeisungsAnfrage from "../../components/haushalte/dashboard/HaushalteEinpeisungsAnfrage";
import HaushaltSmartMeterUpload from "../../components/haushalte/dashboard/HaushaltSmartMeterUpload";
import HaushaltSmartMeterOverview from "../../components/haushalte/dashboard/HaushalteSmartMeterOverview";
import HaushhaltAntragOverview from "../../components/haushalte/dashboard/HaushalteAntragOverview";
import HaushalteEinspeisungsAnfrage from "../../components/haushalte/dashboard/HaushalteEinpeisungsAnfrage";
import HaushalteDataOverview from "../../components/haushalte/dashboard/HaushalteDataOverview";
import HaushalteAngebote from "../../components/haushalte/dashboard/HaushalteAngebote";
import HaushalteHome from "../../components/haushalte/dashboard/HaushalteHome";
import HaushalteVertragWechselnOverview from "../../components/haushalte/dashboard/HaushalteVertragWechselnOverview";
import HaushalteVertragWechselnDetail from "../../components/haushalte/dashboard/HaushalteVertragWechselnDetail";
import HaushalteEnergieAusweisOverview from "../../components/haushalte/dashboard/HaushaltEnergieAusweisOverview";
import HaushalteRechnungenOverview from "../../components/haushalte/dashboard/HaushalteRechnungenOverview";
import HaushalteRechnungenDetail from "../../components/haushalte/dashboard/HaushalteRechnungenDetail";
import FAQ from "../../components/admin/dashboards/FAQs";
import Calendar from "../../components/all/dashboards/Calendar";
import Chat from "../../components/all/Chat.tsx";
import { standardFAQ } from "../../utils/faqs";

const  HaushaltDashboard = () => {
    const [effect, setEffect] = useState("")
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
                <HaushalteSidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true} nutzerrolle={"Haushalte"}/>
                <Routes>
                    <Route path="/tarifTable" element={<HaushalteTarifTable/>}/>
                    <Route path="/" element={<HaushalteHome/>}/>
                    <Route path="/vertragSelect/:tarifID" element={<HaushalteVertragCreate/>}/>
                    <Route path="/vertragOverview" element={<HaushalteVertrag/>}/>  
                    <Route path="/vertragOverview/:vertragID" element={<HaushalteVertragDetail/>}/>
                    <Route path="/einspeisungsanfrage" element={<HaushalteEinpeisungsAnfrage/>}/>
                    <Route path="/pvuploadOverview" element={<HaushaltSmartMeterUpload/>}/>
                    <Route path="/smartMeterOverview" element={<HaushaltSmartMeterOverview/>}/>
                    <Route path="/eispesungsantragOverview" element={<HaushhaltAntragOverview/>}/>    
                    <Route path="/einspeisungsanfrage" element={<HaushalteEinspeisungsAnfrage/>}/>
                    <Route path="/angebote/:anlageID" element={<HaushalteAngebote/>}/>
                    <Route path="/dataOverview" element={<HaushalteDataOverview/>}/>
                    <Route path="/vertragChange/:vertragID" element={<HaushalteVertragWechselnDetail/>}/>
                    <Route path="/vertragChangeOverview/:vertragID" element={<HaushalteVertragWechselnOverview/>}/>

                    <Route path="/rechnungenOverview" element={<HaushalteRechnungenOverview/>}/>
                    <Route path="/rechnungenDetail/:rechnungID" element={<HaushalteRechnungenDetail/>}/>
                    <Route path="/calendar" element={<Calendar/>}/>
                    <Route path="/chat" element={<Chat/>}/>
                    <Route path="/faq" element={<FAQ items={standardFAQ}/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default HaushaltDashboard;