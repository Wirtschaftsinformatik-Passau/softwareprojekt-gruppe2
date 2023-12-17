import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useEffect } from "react";
import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import TableViewIcon from '@mui/icons-material/TableView';
import {Grow} from "@mui/material";
import {CircularProgress} from "@mui/material";
import Header from "../../utility/Header";
import StatBox from "../../utility/visualization/StatBox";
import {setStateOtherwiseRedirect}  from "../../../utils/stateUtils.js"
import BarChart from "../../utility/visualization/BarChart";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";


const NetzHome = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const colors = tokens(theme.palette.mode);
    const [isLoading1, setIsLoading1] = React.useState(true);
    const [tarifData, setTarifData] = React.useState([]);
    const [preisData, setPreisData] = React.useState([]);
    const [laufzeitData, setLaufzeitData] = React.useState([]);
   
    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      setStateOtherwiseRedirect(setTarifData, "netzbetreiber/tarife", navigate,  {Authorization: `Bearer ${token}`})
      setIsLoading1(false);
    }, [])

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      setStateOtherwiseRedirect(setPreisData, "netzbetreiber/preisstrukturen", navigate,  {Authorization: `Bearer ${token}`})
      setIsLoading1(false);
    }, [])

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      setStateOtherwiseRedirect(setLaufzeitData, "netzbetreiber/laufzeit", navigate,  {Authorization: `Bearer ${token}`})
      setIsLoading1(false);
    }, [])

    if (isLoading1) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="300px">
          <CircularProgress />
        </Box>
      );
    }

    return (
        <Box m="20px">
            <Header title="Netzbetreiber Dashboard" subtitle="Für Details die Reiter in der Sidebar auswählen"/>
            <Box display="flex" justifyContent="end" alignItems="center" >
          <Button
            sx={{
              backgroundColor: colors.color1[400],
              color: theme.palette.background.default,
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
              ":hover" : {
                backgroundColor: colors.grey[500],
              
              }
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Download Reports
          </Button>
        </Box>       
        <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px">
        <Grow in={true} timeout={1000}>
        <Box 
        gridColumn={"span 4"} 
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={() => navigate("/admin/roleOverview")}>
        
            <StatBox
            title={Number(tarifData.length)}
            subtitle="Anzahl Tarife gesamt"
            progress="1"
            increase=""
            icon={
              <TableViewIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
        <Box 
        gridColumn={"span 4"} 
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={() => navigate("/admin/roleOverview")}>
        
            <StatBox
            title={Number(preisData.length)}
            subtitle="Anzahl Preisstrukturen gesamt"
            progress="1"
            increase=""
            icon={
              <AttachMoneyIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
        
        </Grow>
        </Box>
        <Box
        display="grid"
        gridTemplateRows="repeat(2, 1fr)"
        gridTemplateColumns={"repeat(6, 1fr)"}
        gridAutoRows="140px"
        gridColumn={"span 3"}
         gridRow={"span 3"}
        gap="0px">
            <Box gridColumn={"span 3"} m="20px">
             <Header title="Laufzeitübersicht der Tarife" variant="h3"/>
             </Box>
             <Box gridColumn={"span 3"} m="20px">
             
             </Box>
            
        <Grow in={true} timeout={1000}>
            <Box 
          
            gridColumn={"span 3"} 
            gridRow={"span 3"}
            display="flex"
            alignItems="center"
            onClick={() => navigate("/admin/roleOverview")}
            sx={{
              cursor: "pointer",
              ":hover":{
                backgroundColor: colors.grey[800],
              }
            }}
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
                <BarChart isDashboard={false} data={laufzeitData} legend="Laufzeit" indexBy="laufzeit"/>
                 </Box>
        </Grow>

        </Box>
        </Box>
    
    )
}

export default NetzHome;