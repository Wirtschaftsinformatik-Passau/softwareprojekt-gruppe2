import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useEffect } from "react";
import React from "react";
import axios from "axios";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import HomeIcon from '@mui/icons-material/Home';
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import LiveHelpIcon from '@mui/icons-material/LiveHelp';
import TrafficIcon from "@mui/icons-material/Traffic";
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import Header from "../../utility/Header";
import LineChart from "../../utility/visualization/LineChart";
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import { Paper } from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import StatBox from "../../utility/visualization/StatBox";
import PieChart from "../../utility/visualization/PieChart";

import { addSuffixToBackendURL } from "../../../utils/networking_utils";


const AdminEndPointActivity = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [numberUsers, setNumberUsers] = React.useState(0);
    const [users, setUsers] = React.useState([])

    useEffect(() => {
       
        axios.get(addSuffixToBackendURL("users"))
        .then((res) => {
          const response = res.data
          setNumberUsers(response.length);
          setUsers(response);
          console.log(Math.round((users.filter((user) => user.rolle === "Admin").length / numberUsers) * 100).toString() )
        })
        .catch((err) => {
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
        <Box 
        gridColumn={"span 6"} 
        display="flex"
        alignItems="center"
        justifyContent="center">
            <StatBox
            title={numberUsers.toString()}
            subtitle="Anzahl Nutzer"
            progress="1"
            increase="+0%"
            icon={
              <PersonOutlinedIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
        <Box 
        gridColumn={"span 3"} 
        display="flex"
        alignItems="center"
        justifyContent="center">
            <Box width="100%" m="0 30px" sx={{background: colors.color1[400], ":hover":{
                background: colors.grey[500],
                cursor: "pointer",
            }}} p="10px" textAlign={"center"}>
            <LiveHelpIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            </Box>
        </Box>
        </Box>
        <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px">
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
              <SolarPowerIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
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
        </Box>
        <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px">
            
        <Box 
        border={"1px solid #E0E0E0"}
        gridRow={"span 2"}
        gridColumn={"span 6"} 
        display="flex"
        alignItems="center"
        boxShadow="0px 4px 4px rgba(0, 0, 0, 0.25)"
        justifyContent="center">
            <PieChart isDashboard={true}/>
             </Box>
        </Box>
        <Box 
        border={"1px solid #E0E0E0"}
        gridColumn={"span 6"} 
        display="flex"
        alignItems="center"
        justifyContent="center">
             </Box>
        </Box>
        


    
    )
}

export default AdminEndPointActivity;