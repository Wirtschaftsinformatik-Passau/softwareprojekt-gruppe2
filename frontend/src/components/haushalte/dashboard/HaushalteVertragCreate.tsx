import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import CircularProgress from '@mui/material/CircularProgress';
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";

interface IVertragPreview {
    beginn_datum: string
    end_datum: string
    jahresabschlag: number
}



const HaushalteVertragCreate = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const {isLoading, setIsLoading} = React.useState(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [vertragPreview, setVertragPreview] = React.useState<IVertragPreview | null>(null)
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [conflictModalIsOpen, setConflictModalIsOpen] = React.useState(false);
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

    const vertragKeyMapping = {
        "beginn_datum": "Beginn Datum",
        "end_datum": "End Datum",
        "jahresabschlag": "Jahresabschlag in Euro"
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
              else if (err.response.status === 409) {
                console.log("Conflict", err.response.data)
                setConflictModalIsOpen(true)
            }
              
              else if (err.response.status === 400) {
                console.log("Bad Request", err.response.data)
                setFailModalIsOpen(true)
              }
            console.log(err)
        })
    }

    const createVertragPreview = () => {
        const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL(`haushalte/vertrag-preview/${tarifID}`), {headers: { Authorization: `Bearer ${token}` }})
        .then((res) => {
            setVertragPreview(res.data)
        })
        .catch((err) => {
            if (err.response.status === 403 || err.response.status === 403) {
                console.log("Unauthorized  oder kein Haushalt", err.response.data)
                navigate("/login")
              }
              else if (err.response.status === 409) {
                console.log("Conflict", err.response.data)
                setConflictModalIsOpen(true)
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
            <Header title={"Detailübersicht Tarif ID "+ tarifID} subtitle="Detaillierte Übersicht über den Tarif. Klicken um Vorschau des vertrags zu sehen."/>
            <Box display={"flex"} justifyContent={"space-evenly"}>
            <Button variant="contained" color="primary" onClick={() => {navigate(-1)}}
                 sx = {{
                    backgroundColor: `${colors.grey[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Abbrechen    
                </Button>
                <Button variant="contained" color="primary" onClick={createVertragPreview}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    Vertrag erstellen    
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
   {vertragPreview != null &&
   <Box m="20px">
    <Header title={"Vertrag Vorschau"} subtitle="Details des ausgewählten Vertrags" variant="h4"/>
    <Box gridTemplateColumns={"repeat(6, minmax(0, 1fr))"} display={"grid"}>
    {Object.entries(vertragPreview).map(([key, value]) => {
        return (
            <Box gridColumn={"span 2"} mt={2} ml={1}>
            <TextField
            fullWidth
            variant="outlined"
            type="text"
            label={vertragKeyMapping[key]}
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
   <Box>
   <Button variant="contained" color="primary" onClick={handleAccept}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default,
                    float: "right",
                    mt: "10px"
                }} >
                    Vertrag bestätigen    
                </Button>
                </Box>
    </Box>
    
}
   
   <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Vertrag erfolgreich erstellt!" navigationGoal="/haushalte"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Antrag fehlgeschlagen"/>
    <SuccessModal open={conflictModalIsOpen} handleClose={() => setConflictModalIsOpen(false)}
    text="Es exisitiert bereits ein Vertrag für diesen Tarif"/>
        </Box>
    )
}

export default HaushalteVertragCreate;