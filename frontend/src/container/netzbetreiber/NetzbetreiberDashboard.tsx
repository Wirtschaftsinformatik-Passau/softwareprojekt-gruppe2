// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";
import Topbar from "../../components/admin/dashboards/Topbar";
import Sidebar from "../../components/netzbetreiber/dashboard/NetzSidebar";
import FAQ from "../../components/admin/dashboards/FAQs";
import NetzHome from "../../components/netzbetreiber/dashboard/NetzHomeDashboard";
import NetzbetreiberTarifCreate from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifCreate";
import NetzbetreiberTarifTable from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifTable.tsx";
import NetzbetreiberTarifEditSelect from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifEditSelect";
import NetzbetreiberTarifEdit from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifEdit";
import NetzbetreiberPreisCreate from "../../components/netzbetreiber/dashboard/NetzbetreiberPreisCreate";
import NetzbetreiberPreisEditSelect from "../../components/netzbetreiber/dashboard/NetzbetreiberPreisEditSelect";
import NetzbetreiberPreisEditCustom from "../../components/netzbetreiber/dashboard/NetzbetreibePreisEditCustom";

const  NetzbetreiberDashboard = () => {
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
                <Sidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true}/>
                <Routes>
                <Route path="/" element={<NetzHome/>}/>
                <Route path="/faq" element={<FAQ items={faqItems}/>}/>
                <Route path="/tarifCreate" element={<NetzbetreiberTarifCreate/>}/>
                <Route path="/tarifTable" element={<NetzbetreiberTarifTable/>}/>
                <Route path="/tarifEdit" element={<NetzbetreiberTarifEditSelect/>}/>
                <Route path="/tarifEdit/:tarifID" element={<NetzbetreiberTarifEdit/>}/>
                <Route path="/priceCreate" element={<NetzbetreiberPreisCreate/>}/>
                <Route path="/priceEdit" element={<NetzbetreiberPreisEditSelect/>}/>
                <Route path="/priceEdit/:priceID" element={<NetzbetreiberPreisEditCustom/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default NetzbetreiberDashboard;