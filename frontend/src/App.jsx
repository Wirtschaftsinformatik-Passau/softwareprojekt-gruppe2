// eslint-disable-next-line no-unused-vars
import {React, useState} from "react";
import {Routes, Route, Navigate} from "react-router-dom";
import {ThemeProvider, CssBaseline } from "@mui/material";
import Registration from "./container/all/Registration.tsx"
import AdminDashboard from "./container/admin/AdminDashboard.jsx";
import Login from "./container/all/Login.tsx"
import LoginUI from "./container/all/LoginUI.tsx"
import { ColorModeContext, useMode } from "./utils/theme.js";


const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [theme, colorMode] = useMode();
    
    return (
        <ColorModeContext.Provider value={useMode()}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <Routes>
            <Route path="/registration" element={<Registration/>}/>
            <Route path="/login" element={<LoginUI/>}/>
            <Route path="/admin" element={<AdminDashboard/>}/>
            <Route path="*" element={
                isLoggedIn ? <Navigate to="/admin"/> : <Navigate to="/login"/>
            }/>
        </Routes>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )
}

export default App
