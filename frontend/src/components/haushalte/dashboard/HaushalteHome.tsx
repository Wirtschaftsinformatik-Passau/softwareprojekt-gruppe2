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
import HomeIcon from '@mui/icons-material/Home';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import {setStateOtherwiseRedirect}  from "../../../utils/stateUtils.js"
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { Vertrag } from "./HaushaltVertrag";
import { PVAntrag } from "../../../entitities/pv";


const NetzHome = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const colors = tokens(theme.palette.mode);
    const [isLoading1, setIsLoading1] = React.useState<boolean>(true);
    const [isLoading2, setIsLoading2] = React.useState<boolean>(true);
    const [vertraege, setVetraege] = React.useState<Vertrag[]>([
        {
            "vertrag_id": 0,
            "user_id": 0,
            "tarif_id":  0,
            "beginn_datum": "",
            "end_datum": "",
            "jahresabschlag": 0,
            "vertragstatus": false,
            "tarifname": "",
            "preis_kwh": 0,
            "grundgebuehr": 0,
            "laufzeit": 0,
            "spezielle_konditionen": "",
            "netzbetreiber_id": 0,
        }
        ]);
    const [antraege, setAntraege] = React.useState<PVAntrag[]>([
        {
            anlage_id: 0,
            haushalt_id: 0,
            solarteur_id: 0,
            prozess_status: "",
            nvpruefung_status: false            
        }
    ]);

    useEffect(() => {
        setStateOtherwiseRedirect(setVetraege, "haushalte/vertraege", navigate, {}, setIsLoading1)
    }, []) ;

    useEffect(() => {
        setStateOtherwiseRedirect(setAntraege, "haushalte/angebot-anfordern", navigate, {}, setIsLoading2);
    }, []);

    



    if (isLoading1 || isLoading2) {
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
            title={Number(vertraege.length)}
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
            title={Number(vertraege.length)}
            subtitle="Laufende Vertraege"
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
            title={Number(vertraege.length)}
            subtitle="Anzahl Haushalte gesamt"
            progress="1"
            increase=""
            icon={
              <HomeIcon
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
        gap="20px">
            <Box gridColumn={"span 3"} m="20px">
             <Header title="Laufzeitübersicht der Tarife" variant="h3"/>
             </Box>
             <Box gridColumn={"span 3"} m="20px">
             <Header title="Geographische Verteilung der Haushalte" variant="h3"/>
             </Box>
            

        </Box>
        </Box>
    
    )
}

export default NetzHome;