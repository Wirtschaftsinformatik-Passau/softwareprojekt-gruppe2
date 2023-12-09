// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";

import Topbar from "../../components/all/dashboards/Topbar";
import Sidebar from "../../components/all/dashboards/AdminSidebar";
import FAQ from "../../components/all/dashboards/FAQs";
import UserCreation from "../../components/all/dashboards/AdminUserCreation";
import AdminUserTable from "../../components/all/dashboards/AdminUserTable";
import AdminUserEdit from "../../components/all/dashboards/AdminUserEdit";


const  AdminDashboard = () => {
    const [effect, setEffect] = useState("")
    const [theme, colorMode] = useMode();
    const faqItems = [
        {
            title: "What is GreenEcoHub?",
            text: "GreenEcoHub is a platform that allows users to track their carbon footprint and compare it to other users. It also allows users to track their progress in reducing their carbon footprint and provides tips on how to reduce it further.",
        }
    ]
    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-screen">
                <Sidebar/>
                <div className="flex-1">
                <Topbar/>
                <Routes>
                <Route path="/faq" element={<FAQ items={faqItems}/>}/>
                <Route path="/userCreation" element={<UserCreation/>}/>
                <Route path="/userTable" element={<AdminUserTable/>}/>
                <Route path="/userEdit/" element={<AdminUserEdit/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default AdminDashboard;