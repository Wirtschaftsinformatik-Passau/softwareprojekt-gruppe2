// eslint-disable-next-line no-unused-vars
import {React, useEffect, useState} from "react";
import {Routes, Route, Navigate} from "react-router-dom";
import {ThemeProvider, CssBaseline } from "@mui/material";
import axios from "axios";
import Registration from "./container/all/Registration.tsx"
import AdminDashboard from "./container/admin/AdminDashboard.tsx";
import NetzbetreiberDashboard from "./container/netzbetreiber/NetzbetreiberDashboard.tsx";
import LoginUI from "./container/all/LoginUI.tsx"
import RegistrationUI from "./container/all/RegistrationUI.tsx";
import { ColorModeContext, useMode } from "./utils/theme.js";
import { addSuffixToBackendURL } from "./utils/networking_utils.js";



const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [theme, colorMode] = useMode();
    
    useEffect(() => {  
      const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("users/current/single"), {headers: {Authorization: `Bearer ${token}`}})
        .then((res) => {
          setIsLoggedIn(true)
        })
        .catch((err) => {

          setIsLoggedIn(false)
        })  
    },[])

    console.log("is logged in or not ")
    console.log(isLoggedIn)
    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
                
        <Routes>
            <Route path="/registration" element={<RegistrationUI/>}/>
            <Route path="/login" element={<LoginUI isAlreadyLoggedIn={isLoggedIn} />}/>
            <Route path="/admin/*" element={<AdminDashboard/>}/>
            <Route path="/netzbetreiber/*" element={<NetzbetreiberDashboard/>}/>
            <Route path="*" element={<LoginUI isAlreadyLoggedIn={isLoggedIn}/>}/>
        </Routes>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )
}

export default App
