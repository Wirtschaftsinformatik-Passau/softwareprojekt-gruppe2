// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import {Routes, Route, Navigate} from "react-router-dom";
import { ColorModeContext, useMode } from "../../utils/theme";

import Topbar from "../../components/all/Topbar"
import Sidebar from "../../components/admin/dashboards/AdminSidebar";
import FAQ from "../../components/admin/dashboards/FAQs";
import UserCreation from "../../components/admin/dashboards/AdminCreateUser";
import AdminUserTable from "../../components/admin/dashboards/AdminUserTable";
import AdminEndPointActivity from "../../components/admin/dashboards/AdminEndPointAcitvity";
import AdminRoleOverview from "../../components/admin/dashboards/AdminRoleOverview";
import AdminHomeDashboard from "../../components/admin/dashboards/AdminHomeDashboard";
import AdminLogOverview from "../../components/admin/dashboards/AdminLogOverview";
import Calendar from "../../components/all/dashboards/Calendar";
import AdminUserEditSelect from "../../components/admin/dashboards/AdminUserEditSelect";
import AdminUserEditCustom from "../../components/admin/dashboards/AdminUserEditCustom";
import Chat from "../../components/all/Chat";
import { standardFAQ } from "../../utils/faqs";


const  AdminDashboard = () => {
    const [effect, setEffect] = useState("")
    const [theme, colorMode] = useMode();

    

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-100" style={{marginTop: "64px"}}>
                <Sidebar/>
                <div className="flex-1 overflow-y-auto">
                <Topbar fixed={true} nutzerrolle={"Admin"}/>
                <Routes>
                <Route path="/" element={<AdminHomeDashboard/>}/>
                <Route path="/faq" element={<FAQ items={standardFAQ}/>}/>
                <Route path="/chat" element={<Chat/>}/>
                <Route path="/userCreation" element={<UserCreation/>}/>
                <Route path="/userTable" element={<AdminUserTable/>}/>
                <Route path="/editUser/" element={<AdminUserEditSelect/>}/>
                <Route path="/editUser/:userId" element={<AdminUserEditCustom/>}/>
                <Route path="/endpointActivity" element={<AdminEndPointActivity/>}/>
                <Route path="/roleOverview" element={<AdminRoleOverview/>}/>
                <Route path="/logOverview" element={<AdminLogOverview/>}/>
                <Route path="/calendar" element={<Calendar/>}/>
                </Routes>
                </div>
                
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default AdminDashboard;