// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";

import Topbar from "../../components/admin/dashboards/Topbar";
import Sidebar from "../../components/admin/dashboards/AdminSidebar";
import FAQ from "../../components/admin/dashboards/FAQs";
import UserCreation from "../../components/admin/dashboards/AdminCreateUser";
import AdminUserTable from "../../components/admin/dashboards/AdminUserTable";
import AdminUserEdit from "../../components/admin/dashboards/AdminUserEdit";
import AdminEndPointActivity from "../../components/admin/dashboards/AdminEndPointAcitvity";
import AdminRoleOverview from "../../components/admin/dashboards/AdminRoleOverview";
import AdminHomeDashboard from "../../components/admin/dashboards/AdminHomeDashboard";


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
        <div className="flex h-100">
                <Sidebar/>
                <div className="flex-1">
                <Topbar/>
                <Routes>
                <Route path="/" element={<AdminHomeDashboard/>}/>
                <Route path="/faq" element={<FAQ items={faqItems}/>}/>
                <Route path="/userCreation" element={<UserCreation/>}/>
                <Route path="/userTable" element={<AdminUserTable/>}/>
                <Route path="/editUser/" element={<AdminUserEdit/>}/>
                <Route path="/endpointActivity" element={<AdminEndPointActivity/>}/>
                <Route path="/roleOverview" element={<AdminRoleOverview/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default AdminDashboard;