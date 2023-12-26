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
    const {anlageID} = useParams();
    const [antrag, setAntrag] = React.useState({
        "anlage_id": "",
    "haushalt_id": "",
    "solarteur_id": "",
    "modultyp": null,
    "kapazitaet": null,
    "installationsflaeche": null,
    "installationsdatum": null,
    "modulanordnung": null,
    "kabelwegfuehrung": null,
    "montagesystem": null,
    "schattenanalyse": null,
    "wechselrichterposition": null,
    "installationsplan": null,
    "prozess_status": "",
    "nvpruefung_status": null
    })

    const keyMapping = {
        "anlage_id": "Anlage ID",
        "haushalt_id": "Haushalt ID",
        "solarteur_id": "Solarteur ID",
        "modultyp": "Modultyp",
        "kapazitaet": "Kapazität",
        "installationsflaeche": "Installationsfläche",
        "installationsdatum": "Installationsdatum",
        "modulanordnung": "Modulanordnung",
        "kabelwegfuehrung": "Kabelwegführung",
        "montagesystem": "Montagesystem",
        "schattenanalyse": "Schattenanalyse",
        "wechselrichterposition": "Wechselrichterposition",
        "installationsplan": "Installationsplan",
        "prozess_status": "Prozess Status",
        "nvpruefung_status": "Netzverträglichkeitsprüfung Status"

    }

    const navigate = useNavigate();

    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setAntrag, "netzbetreiber/einspeisezusagen/"+anlageID , 
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []
    )

    const handleAccept = () => { 
        const token = localStorage.getItem("accessToken");
        console.log(token)
        axios.put(addSuffixToBackendURL(`netzbetreiber/einspeisezusage/${anlageID}`), {}, {headers: { Authorization: `Bearer ${token}` }})
        .then((res) => {
            console.log("success")
            setSuccessModalIsOpen(true)
        })
        .catch((err) => {
            if (err.response.status === 403 || err.response.status === 403) {
                console.log("Unauthorized  oder kein Netzbetreiber", err.response.data)
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
            <Header title={"Detailübersicht Anlage ID "+ anlageID} subtitle="Detaillierte Übersicht über Einspeisungsanfrage"/>
            <Box display={"flex"} justifyContent={"space-evenly"}>
            <Button variant="contained" color="primary" onClick={() => {navigate("/netzbetreiber/einspeisungenOverview")}}
                 sx = {{
                    backgroundColor: `${colors.grey[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Abbrechen    
                </Button>
                <Button variant="contained" color="primary" onClick={() => {}}
                 sx = {{
                    backgroundColor: `${colors.color5[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Anfrage ablehnen    
                </Button>
                <Button variant="contained" color="primary" onClick={handleAccept}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    Anfrage annehmen    
                </Button>

            </Box>
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
    {Object.entries(antrag).map(([key, value]) => {
        return (
            <Box gridColumn={"span 2"} mt={2} ml={1}>
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
    text="Einspeisezusage erfolgreich erteilt!" navigationGoal="/netzbetreiber"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Netzverträglichkeitsprüfung fehlgeschlagen"/>
        </Box>
    )
}

export default NetzbetreiberEinspeisungenZusage;