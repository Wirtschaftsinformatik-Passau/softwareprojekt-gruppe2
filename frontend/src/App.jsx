// eslint-disable-next-line no-unused-vars
import {React, useEffect, useState} from "react";
import {Routes, Route, Navigate} from "react-router-dom";
import {ThemeProvider, CssBaseline } from "@mui/material";
import axios from "axios";
import AdminDashboard from "./container/admin/AdminDashboard.tsx";
import NetzbetreiberDashboard from "./container/netzbetreiber/NetzbetreiberDashboard.tsx";
import HaushaltDashboard from "./container/haushalte/HaushaltDashboard.tsx";
import SolarteureDashboard from "./container/solarteure/SolarteureDashboard.tsx";
import EnergieberatendeDashboard from "./container/energieberatende/EnergieberatendeDashboard.tsx";
import ImpressumPage from "./container/all/Impressum.tsx";
import LoginUI from "./container/all/LoginUI.tsx"
import RegistrationUI from "./container/all/RegistrationUI.tsx";
import Chat from "./components/all/Chat.tsx";
import Profile from "./container/all/Profile.tsx";
import PasswordReset from "./container/all/PasswordReset.tsx";
import { ColorModeContext, useMode } from "./utils/theme.js";
import { addSuffixToBackendURL } from "./utils/networking_utils.js";



const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [theme, colorMode] = useMode();
    
    useEffect(() => {  
      try {
      const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("users/current/single"), {headers: {Authorization: `Bearer ${token}`}})
        .then((res) => {
          setIsLoggedIn(true)
        })
        .catch((err) => {

          setIsLoggedIn(false)
        })  
      }
      catch(err) {
        setIsLoggedIn(false)
      }
    },[])

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
                
        <Routes>
            <Route path="/registration" element={<RegistrationUI/>}/>
            <Route path="/login" element={<LoginUI isAlreadyLoggedIn={isLoggedIn} />}/>
            <Route path="/admin/*" element={<AdminDashboard/>}/>
            <Route path="/netzbetreiber/*" element={<NetzbetreiberDashboard/>}/>
            <Route path="/haushalte/*" element={<HaushaltDashboard/>}/>
            <Route path="/solarteure/*" element={<SolarteureDashboard/>}/>
            <Route path="/energieberatende/*" element={<EnergieberatendeDashboard/>}/>
            <Route path="/profile"  element={<Profile/>}/>
            <Route path="/reset-password/:token" element={<PasswordReset/>}/>
            <Route path="/impressum" element={<ImpressumPage/>}/>
            <Route path="*" element={<LoginUI isAlreadyLoggedIn={isLoggedIn}/>}/>
        </Routes>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )
}

export default App