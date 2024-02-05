// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";
import Topbar from "../../components/all/Topbar"
import Sidebar from "../../components/netzbetreiber/dashboard/NetzSidebar";
import FAQ from "../../components/admin/dashboards/FAQs";
import NetzHome from "../../components/netzbetreiber/dashboard/NetzHomeDashboard";
import NetzbetreiberTarifCreate from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifCreate";
import NetzbetreiberTarifTable from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifTable";
import NetzbetreiberTarifEditSelect from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifEditSelect";
import NetzbetreiberTarifEdit from "../../components/netzbetreiber/dashboard/NetzbetreiberTarifEdit";
import NetzbetreiberPreisCreate from "../../components/netzbetreiber/dashboard/NetzbetreiberPreisCreate";
import NetzbetreiberPreisEditSelect from "../../components/netzbetreiber/dashboard/NetzbetreiberPreisEditSelect";
import NetzbetreiberPreisEditCustom from "../../components/netzbetreiber/dashboard/NetzbetreibePreisEditCustom";
import NetzbetreiberPreisTable from "../../components/netzbetreiber/dashboard/NetzbetreiberPreisTable";
import NetzbetreiberSmartmeterOverview from "../../components/netzbetreiber/dashboard/NetzbetreiberSmartmeterOverview";
import NetzbetreiberHaushalteTable from "../../components/netzbetreiber/dashboard/NetzbetreiberHaushalteTable";
import NetzbetreiberEinspeisungenTable from "../../components/netzbetreiber/dashboard/NetzbetreiberEinspeisungenTable";
import NetzbetreiberEinspeisungenAngenommen from "../../components/netzbetreiber/dashboard/NetzbetreiberEinspeisungenAngenommen";
import NetzbetreiberSmartmeterUpload from "../../components/netzbetreiber/dashboard/NetzbetreiberSmartMeterUpload"
import NetzbetreiberLaufendeVertraege from "../../components/netzbetreiber/dashboard/NetzbetreiberLaufendeVertraege"
import NetzbetreiberKuendigungsAnfragen from "../../components/netzbetreiber/dashboard/NetzbetreiberKuendigungsAnfragen"
import NetzbetreiberVertragDetail from"../../components/netzbetreiber/dashboard/NetzbetreiberVertragDetail"
import NetzbertreiberEinspeisungenDetail from "../../components/netzbetreiber/dashboard/NetzbetreiberEinspeisungenDetail";
import NetzbetreiberMitarbeiterTable from "../../components/netzbetreiber/dashboard/NetzbetreiberMitarbeiterTable";
import NetzbetreiberMitarbeiterCreate from "../../components/netzbetreiber/dashboard/NetzbetreiberMitarbeiterCreate";
import EnergieberaterRechnungsTable from "../../components/energieberatende/dashboard/EnergieberatendeRechnungenOverview";
import Chat from "../../components/all/Chat";
import Calendar from "../../components/all/dashboards/Calendar";
import { standardFAQ } from "../../utils/faqs";

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
                <Topbar fixed={true} nutzerrolle={"Netzbetreiber"}/>
                <Routes>
                <Route path="/" element={<NetzHome/>}/>
                <Route path="/tarifCreate" element={<NetzbetreiberTarifCreate/>}/>
                <Route path="/tarifTable" element={<NetzbetreiberTarifTable/>}/>
                <Route path="/tarifEdit" element={<NetzbetreiberTarifEditSelect/>}/>
                <Route path="/tarifEdit/:tarifID" element={<NetzbetreiberTarifEdit/>}/>
                <Route path="/priceCreate" element={<NetzbetreiberPreisCreate/>}/>
                <Route path="/priceEdit" element={<NetzbetreiberPreisEditSelect/>}/>
                <Route path="/priceEdit/:priceID" element={<NetzbetreiberPreisEditCustom/>}/>
                <Route path="/priceTable" element={<NetzbetreiberPreisTable/>}/>
                <Route path="/smartmeterOverview" element={<NetzbetreiberSmartmeterOverview/>}/>
                <Route path="/haushalteOverview" element={<NetzbetreiberHaushalteTable/>}/>
                <Route path="/einspeisungen" element={<NetzbetreiberEinspeisungenTable/>}/>
                <Route path="/einspeisungen/:anlageID" element={<NetzbertreiberEinspeisungenDetail/>}/>
                <Route path="/einspeisungenAngenommen" element={<NetzbetreiberEinspeisungenAngenommen/>}/>
                <Route path="/smartmeterUpload" element={<NetzbetreiberSmartmeterUpload/>}/>
                <Route path="/vertraege" element={<NetzbetreiberLaufendeVertraege/>}/>
                <Route path="/vertraegeKuendigung" element={<NetzbetreiberKuendigungsAnfragen/>}/>
                <Route path="vertraege/:vertragID" element={<NetzbetreiberVertragDetail/>}/>
                <Route path="/mitarbeiterTable" element={<NetzbetreiberMitarbeiterTable/>}/>
                <Route path="/mitarbeiterCreate" element={<NetzbetreiberMitarbeiterCreate/>}/>
                <Route path="/rechnungenOverview" element={<EnergieberaterRechnungsTable/>}/>
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

export default NetzbetreiberDashboard;