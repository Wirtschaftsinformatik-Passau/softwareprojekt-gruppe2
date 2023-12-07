// @ts-ignore
// eslint-disable-next-line no-unused-vars
import React, {useState} from "react";
import Topbar from "../../components/all/dashboards/Topbar";
import Sidebar from "../../components/all/dashboards/Sidebar";
import { Box, Typography } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { ColorModeContext, useMode } from "../../utils/theme";

const  AdminDashboard = () => {
    const [effect, setEffect] = useState("")
    const [theme, colorMode] = useMode();

    return (
        <ColorModeContext.Provider value={useMode()}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
        <div className="flex h-screen">
                <Sidebar/>
                <div className="flex-1">
                <Topbar/>
                </div>
        </div>
        </ThemeProvider>
        </ColorModeContext.Provider>
    )

}

export default AdminDashboard;