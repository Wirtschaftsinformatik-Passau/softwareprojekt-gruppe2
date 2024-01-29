import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useEffect } from "react";
import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import TableViewIcon from '@mui/icons-material/TableView';
import {Grow} from "@mui/material";
import {CircularProgress} from "@mui/material";
import Header from "../../utility/Header";
import StatBox from "../../utility/visualization/StatBox";
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import {setStateOtherwiseRedirect}  from "../../../utils/stateUtils.js"
import { SolarteurResponse } from "../../../entitities/pv";

const EnergieHome = () => {
  const theme = useTheme();
  const colors: Object = tokens(theme.palette.mode);
  const [dataOffen, setDataOffen] = React.useState<SolarteurResponse[]>([]);
  const [dataBearbeitet, setDataBearbeitet] = React.useState<SolarteurResponse[]>([]);
  const [dataAgeschlossen, setDataAbgeschlossen] = React.useState<SolarteurResponse[]>([]);
  const [isLoading1, setIsLoading1] = React.useState<boolean>(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setDataOffen, "energieberatende/anfragen?prozess_status=AusweisAngefordert",
     navigate,  {Authorization: `Bearer ${token}`})
     setIsLoading1(false);
  }, [])

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setDataAbgeschlossen, "energieberatende/anfragen?prozess_status=Abgenommen",    
     navigate,  {Authorization: `Bearer ${token}`})
  }, [])

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setDataBearbeitet, "energieberatende/anfragen?prozess_status=PlanErstellt&prozess_status=PlanErstellt&prozess_status=AusweisErstellt&prozess_status=Genehmigt",
     navigate,  {Authorization: `Bearer ${token}`})
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
            <Header title="Energieberatende Dashboard" subtitle="Für Details die Reiter in der Sidebar auswählen"/>
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
        onClick={() => navigate("/energieberatende/antragTable")}>
        
            <StatBox
            title={Number(dataOffen.length)}
            subtitle="Offene PV Anträge"
            progress="1"
            increase=""
            icon={
              <TrackChangesIcon
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
        onClick={() => navigate("/energieberatende/antragTableBearbeitet")}>
        
            <StatBox
            title={Number(dataBearbeitet.length)}
            subtitle="Bearbeitete Antraege"
            progress="1"
            increase=""
            icon={
              <AccessTimeIcon
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
        onClick={() => navigate("/energieberatende/antragTableAbgeschlossen")}>
        
            <StatBox
            title={Number(dataAgeschlossen.length)}
            subtitle="Abgeschlossene Antraege"
            progress="1"
            increase=""
            icon={
              <CheckBoxIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
        
        </Grow>
        <Grow in={true} timeout={1000}>
        <Box 
        gridColumn={"span 6"} 
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={() => navigate("/energieberatende/rechnungenOverview")}>
        
            <StatBox
            title={"Rechnungen einsehen"}
            subtitle=""
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
        <Grow in={true} timeout={1000}>
        <Box 
        gridColumn={"span 6"} 
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={() => navigate("/energieberatende/calendar")}>
        
            <StatBox
            title={"Kalender aufrufen"}
            subtitle=""
            progress="1"
            increase=""
            icon={
              <CalendarTodayOutlinedIcon
                sx={{ color: theme.palette.background.default, fontSize: "26px"}}
              />
            }
          />
        </Box>
        
        </Grow>
        
        </Box>
        </Box>
    
    )
}

export default EnergieHome;