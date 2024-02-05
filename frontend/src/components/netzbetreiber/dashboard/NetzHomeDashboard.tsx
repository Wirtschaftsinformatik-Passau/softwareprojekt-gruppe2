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
import {setStateOtherwiseRedirect}  from "../../../utils/stateUtils.js"
import BarChart from "../../utility/visualization/BarChart";
import LeafletGeo   from "../../utility/visualization/LeafletGeo";
import PublicIcon from '@mui/icons-material/Public';
import { addSuffixToBackendURL } from "../../../utils/networking_utils"
import SuccessModal from "../../utility/SuccessModal";
import FullLoadingSpinner from "../../utility/FullLoadingSpinner";


const NetzHome = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const colors = tokens(theme.palette.mode);
    const [isLoading1, setIsLoading1] = React.useState(true);
    const [tarifData, setTarifData] = React.useState([]);
    const [preisData, setPreisData] = React.useState([]);
    const [laufzeitData, setLaufzeitData] = React.useState([]);
    const [isLoading2, setIsLoading2] = React.useState(false);
    const [haushalte, setHaushalte] = React.useState([]);
    const [geocodeFail, setGeocodeFail] = React.useState(false);
    const [geoCodeSuccess, setGeoCodeSuccess] = React.useState(false);
    const [geoData, setGeoData] = React.useState([
      { id: '1', position: [48.57408564310167, 13.463277360121875], name: '1' }]);
   
    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      setStateOtherwiseRedirect(setTarifData, "netzbetreiber/tarife", navigate,  {Authorization: `Bearer ${token}`})
      setIsLoading1(false);
    }, [])

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      setStateOtherwiseRedirect(setGeoData, "users/adresse", navigate,  {Authorization: `Bearer ${token}`})
      setIsLoading1(false);
    }, [geoCodeSuccess])

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

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      setStateOtherwiseRedirect(setHaushalte, "netzbetreiber/haushalte", navigate,  {Authorization: `Bearer ${token}`})
      setIsLoading1(false);
    }, [])

    const geocodieren = () => {
      const token = localStorage.getItem("accessToken");
      setIsLoading2(true);
      axios.post(addSuffixToBackendURL("users/geocode"),{}, {headers: {Authorization: `Bearer ${token}`}})
      .then((response) => {
       setIsLoading2(false);
        setGeoCodeSuccess(true);

      })
      .catch((error) => {
        setIsLoading2(false);
        setGeocodeFail(true);
      });
    }


    if (isLoading1) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="300px">
          <CircularProgress />
        </Box>
      );
    }

    if (isLoading2) {
      return (
        <FullLoadingSpinner />
      );
    }

    return (
        <Box m="20px">
            <Header title="Netzbetreiber Dashboard" subtitle="Für Details die Reiter in der Sidebar auswählen"/>
            <Box display="flex" justifyContent="end" alignItems="center" >
            <Button
            onClick={() => geocodieren()}
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
            <PublicIcon sx={{ mr: "10px" }} />
            Adressen geocodieren
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
        <Grow in={true} timeout={1000}>
        <Box 
        gridColumn={"span 4"} 
        display="flex"
        alignItems="center"
        justifyContent="center"
        onClick={() => navigate("/admin/roleOverview")}>
        
            <StatBox
            title={Number(haushalte.length)}
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
            
        <Grow in={true} timeout={1000}>
            <Box 
          
            gridColumn={"span 3"} 
            gridRow={"span 3"}
            border={"1px solid grey"}
            display="flex"
            alignItems="center"
            sx={{
              cursor: "pointer",
              ":hover":{
                backgroundColor: colors.grey[800],
              }
            }}
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
                <BarChart isDashboard={false} data={laufzeitData} legend="Laufzeit" indexBy="laufzeit" ylabel="Anzahl"/>
                 </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
          
            gridColumn={"span 3"} 
            gridRow={"span 3"}
            display="flex"
            alignItems="center"
            sx={{
              cursor: "pointer",
              ":hover":{
                backgroundColor: colors.grey[800],
              }
            }}
          
            borderRadius={"15px"}
            border={"1px solid grey"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
                <LeafletGeo locations={geoData}/>
                 </Box>
        </Grow>

        </Box>
        <SuccessModal open={geoCodeSuccess} handleClose={() => setGeoCodeSuccess(false)} 
    text="Geokodierung erfolgreich!"/>
     <SuccessModal open={geocodeFail} handleClose={() => setGeocodeFail(false)} 
    text="Geokodierung fehlgeschlagen!"/>
        </Box>
    
    )
}

export default NetzHome;