import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useEffect } from "react";
import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import PowerIcon from '@mui/icons-material/Power';
import HomeIcon from '@mui/icons-material/Home';
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import LiveHelpIcon from '@mui/icons-material/LiveHelp';
import TrafficIcon from "@mui/icons-material/Traffic";
import {Fade} from "@mui/material";
import Grow from "@mui/material/Grow";
import {Collapse} from "@mui/material";
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import Header from "../../utility/Header";
import LineChart from "../../utility/visualization/LineChart";
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import { Paper } from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import StatBox from "../../utility/visualization/StatBox";
import PieChart from "../../utility/visualization/PieChart";
import BarChart from "../../utility/visualization/BarChart";

import { addSuffixToBackendURL } from "../../../utils/networking_utils";


const AdminEndPointActivity = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const colors = tokens(theme.palette.mode);
    const [numberUsers, setNumberUsers] = React.useState(0);
    const [users, setUsers] = React.useState([])

    useEffect(() => {
       
      const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("users"), {headers: { Authorization: `Bearer ${token}` }})
        .then((res) => {
          const response = res.data
          setNumberUsers(response.length)
          setUsers(response);
          console.log(Math.round((users.filter((user) => user.rolle === "Admin").length / numberUsers) * 100).toString() )
        })
        .catch((err) => {
          if (err.response.status === 401) {
            navigate("/login");
          }
          else if (err.response.status === 403) {
            //navigate("/login");

          }
          console.log(err.response.data)
        })
      
      }, [])
    
      console.log(numberUsers)

    return (
        <Box m="20px">
            <Header title="Admin Dashboard" subtitle="Für Details die Reiter in der Sidebar auswählen"/>
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
        gridColumn={"span 6"} 
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={() => navigate("/admin/roleOverview")}>
        
            <StatBox
            title={numberUsers.toString()}
            subtitle="Anzahl Nutzer gesamt"
            progress="1"
            increase="+0%"
            icon={
              <PersonOutlinedIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
        </Grow>
        
        </Box>
        <Box
        display="grid"
        gridTemplateColumns="repeat(15, 1fr)"
        gridAutoRows="140px"
        gap="20px">
        <Grow in={true} timeout={1000}>
            <Box 
            gridColumn={"span 3"} 
            display="flex"
            alignItems="center"
            justifyContent="center">
                <StatBox
                title={users.filter((user) => user.rolle === "Admin").length.toString()}
                subtitle="Admins"
                progress= {(Math.round((users.filter((user) => user.rolle === "Admin").length / numberUsers) * 100) / 100).toString()}
                increase="+0%"
                icon={
                  <AdminPanelSettingsIcon
                    sx={{ color: theme.palette.background.default, fontSize: "26px"}}
                  />
                }
              />
            </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
            gridColumn={"span 3"} 
            display="flex"
            alignItems="center"
            justifyContent="center">
                <StatBox
                title={users.filter((user) => user.rolle === "Solateur").length.toString()}
                subtitle="Solateure"
                progress= {(Math.round((users.filter((user) => user.rolle === "Solateur").length / numberUsers) * 100) / 100).toString()}
                increase="+0%"
                icon={
                  <SolarPowerIcon
                    sx={{ color: theme.palette.background.default, fontSize: "26px"}}
                  />
                }
              />
            </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
            gridColumn={"span 3"} 
            display="flex"
            alignItems="center"
            justifyContent="center">
                <StatBox
                title={users.filter((user) => user.rolle === "Energieberatende").length.toString()}
                subtitle="Energieberater"
                progress= {(Math.round((users.filter((user) => user.rolle === "Energieberatende").length / numberUsers) * 100) / 100).toString()}
                increase="+0%"
                icon={
                  <PointOfSaleIcon
                    sx={{ color: theme.palette.background.default, fontSize: "26px"}}
                  />
                }
              />
            </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
            gridColumn={"span 3"} 
            display="flex"
            alignItems="center"
            justifyContent="center">
                <StatBox
                title={users.filter((user) => user.rolle === "Haushalte").length.toString()}
                subtitle="Haushalte"
                progress= {(Math.round((users.filter((user) => user.rolle === "Haushalte").length / numberUsers) * 100) / 100).toString()}
                increase="+0%"
                icon={
                  <HomeIcon
                    sx={{ color: theme.palette.background.default, fontSize: "26px"}}
                  />
                }
              />
              </Box>
              
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
            gridColumn={"span 3"} 
            display="flex"
            alignItems="center"
            justifyContent="center">
                <StatBox
                title={users.filter((user) => user.rolle === "Netzbetreiber").length.toString()}
                subtitle="Netzbetreiber"
                progress= {(Math.round((users.filter((user) => user.rolle === "Netzbetreiber").length / numberUsers) * 100) / 100).toString()}
                increase="+0%"
                icon={
                  <PowerIcon
                    sx={{ color: theme.palette.background.default, fontSize: "26px"}}
                  />
                }
              />
              </Box>
              
        </Grow>
        </Box>
        <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px">  
        <Box
        display="grid"
        gridTemplateRows="repeat(2, 1fr)"
        gridAutoRows="140px"
        gridColumn={"span 6"}
        gridRow={"span 3"}
        gap="0px">
            <Box gridColumn={"span 6"} m="20px">
             <Header title="Endpunktaktivität" variant="h3"/>
             </Box>
            
        <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 3"}
            gridColumn={"span 6"} 
            display="flex"
            alignItems="center"
            onClick={() => navigate("/admin/endpointActivity")}
            sx={{
              cursor: "pointer",
              ":hover":{
                backgroundColor: colors.grey[800],
              }
            }}
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <LineChart isDashboard={true}/>
                 </Box>
        </Grow>

        </Box>
    
        <Box
        display="grid"
        gridTemplateRows="repeat(2, 1fr)"
        gridAutoRows="140px"
        gridColumn={"span 6"}
         gridRow={"span 3"}
        gap="0px">
            <Box gridColumn={"span 6"} m="20px">
             <Header title="Rollenübersicht" variant="h3"/>
             </Box>
            
        <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 3"}
            gridColumn={"span 6"} 
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
               
                <PieChart isDashboard={true}/>
                 </Box>
        </Grow>

        </Box>

        </Box>
        
  
        </Box>
        


    
    )
}

export default AdminEndPointActivity;