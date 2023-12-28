import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import {MenuItem, Select, FormControl, InputLabel, FormHelperText} from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import useMediaQuery from "@mui/material/useMediaQuery";
import SuccessModal from "../../utility/SuccessModal";
import {IUser, User, Nutzerrolle, UserDropDownOption} from "../../../entitities/user"
import axios from "axios";
import { Iadresse, Adresse } from "../../../entitities/adress";
import CircularProgress from '@mui/material/CircularProgress';
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { h } from "@fullcalendar/core/preact";
import { s } from "@fullcalendar/core/internal-common";




const NetzbetreiberEinspeisungenZusage = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const {isLoading, setIsLoading} = React.useState(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const {tarifID} = useParams();
    const [tarif, setTarif] = React.useState({
            "vorname": "",
            "nachname": "",
            "email": "",
            "preis_kwh": "",
            "tarif_id": "",
            "laufzeit": "",
            "netzbetreiber_id": "101",
            "tarifname": "",
            "grundgebuehr": "",
            "spezielle_konditionen": ""
        
    })

    const keyMapping = {
        "vorname": "Vorname Netzbetreiber",
        "nachname": "Nachname Netzbertreiber",
        "email": "E-Mail Netzbetreiber",
        "preis_kwh": "Preis pro kWh",
        "tarif_id": "Tarif ID",
        "laufzeit": "Laufzeit in Jahren",
        "netzbetreiber_id": "Netzbetreiber ID",
        "tarifname": "Tarifname",
        "grundgebuehr": "Grundgebühr",
        "spezielle_konditionen": "Spezielle Konditionen"

    }

    const navigate = useNavigate();

    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setTarif, "haushalte/all-tarife/"+tarifID , 
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []
    )

    const handleAccept = () => { 
        const token = localStorage.getItem("accessToken");
        axios.post(addSuffixToBackendURL(`haushalte/tarifantrag/${tarifID}`), {}, {headers: { Authorization: `Bearer ${token}` }})
        .then((res) => {
            console.log("success")
            setSuccessModalIsOpen(true)
        })
        .catch((err) => {
            if (err.response.status === 403 || err.response.status === 403) {
                console.log("Unauthorized  oder kein Haushalt", err.response.data)
                navigate("/login")
              }
              else if (err.response.status === 400) {
                console.log("Bad Request", err.response.data)
                setFailModalIsOpen(true)
              }
            console.log(err)
        })
    }

    if (isLoading) {
        return (
          <Box display="flex" justifyContent="center" alignItems="center" height="300px">
            <CircularProgress />
          </Box>
        );
      }

    return (
        <Box m="20px">
            <Header title={"Detailübersicht Tarif ID "+ tarifID} subtitle="Detaillierte Übersicht über Einspeisungsanfrage"/>
            <Box display={"flex"} justifyContent={"space-evenly"}>
            <Button variant="contained" color="primary" onClick={() => {navigate(-1)}}
                 sx = {{
                    backgroundColor: `${colors.grey[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Abbrechen    
                </Button>
                <Button variant="contained" color="primary" onClick={handleAccept}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    Vertrag abschließen    
                </Button>

            </Box>
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
    {Object.entries(tarif).map(([key, value]) => {
        return (
            <Box gridColumn={key === "spezielle_konditionen" ? "span 4" : "span 2"} mt={2} ml={1}>
            <TextField
            fullWidth
            variant="outlined"
            type="text"
            label={keyMapping[key]}
            name={key}
            value={value}
            disabled
            
            InputLabelProps={{
              style: { color: `${colors.color1[500]}` },
          }}
          sx={{
              gridColumn: "span 2",
              '& .MuiInputBase-input': { 
                  color: `${colors.color1[500]} !important`,
        
              },
              '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: `${colors.color1[500]} !important`,
              },
              '& .Mui-disabled': {
                color: `${colors.color1[500]} !important`,
              },
              '& .MuiInputBase-input.Mui-disabled': {
                opacity: 1, 
                WebkitTextFillColor: `${colors.color1[500]} !important` 
              }
              
          }} />
          </Box>
        )
    })}
   </Box>
   <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Vertrag erfolgreich erstellt!" navigationGoal="/netzbetreiber"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Antrag fehlgeschlagen"/>
        </Box>
    )
}

export default NetzbetreiberEinspeisungenZusage;