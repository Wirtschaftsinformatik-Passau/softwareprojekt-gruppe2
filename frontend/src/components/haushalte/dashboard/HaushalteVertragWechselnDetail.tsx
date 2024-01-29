import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams, useSearchParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import CircularProgress from '@mui/material/CircularProgress';
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { AntwortOptionen } from "../../netzbetreiber/dashboard/NetzbetreiberVertragDetail";

interface IVertragPreview {
    beginn_datum: string
    end_datum: string
    jahresabschlag: number
}



const HaushalteVertragWechselnDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const {isLoading, setIsLoading} = React.useState(true);
    const tarifID = useParams();
    const [denyModalIsOpen, setDenyModalIsOpen] = React.useState<boolean>(false);
    const [searchParams, setSearchParams] = useSearchParams();
    const oldTarifID = searchParams.get("oldTarifID");
    const newTarifID = searchParams.get("newTarifID");
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [vertragPreview, setVertragPreview] = React.useState<IVertragPreview | null>(null)
    const [conflictModalIsOpen, setConflictModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const vertragID = useParams();
    console.log(vertragID)
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
    const [oldTarif, setOldTarif] = React.useState({
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
        console.log(tarifID)
        setStateOtherwiseRedirect(setTarif, "haushalte/all-tarife/"+newTarifID, 
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []
    )

    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setOldTarif, "haushalte/all-tarife/"+oldTarifID , 
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []
    )

    const handleKuendigung = () => {
        const token = localStorage.getItem("accessToken");
        axios.post(addSuffixToBackendURL(`haushalte/kuendigungsanfrage/${vertragID.vertragID}?neuer_tarif_id=${newTarifID}`), {}, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }).then((response) => {
            setSuccessModalIsOpen(true);
        }).catch((error) => {
            setFailModalIsOpen(true);
        })
    }


    const createVertragPreview = () => {
        const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL(`haushalte/vertrag-preview/${newTarifID}`), {headers: { Authorization: `Bearer ${token}` }})
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
            <Header title={"Aktueller Tarif"} subtitle="Der zum aktuellen Vertrag laufende Tarif."/>
            <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"} mb={"30px"}>
            {Object.entries(oldTarif).map(([key, value]) => {
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
            <Header title={"Neuer Tarif"} subtitle="Übersicht über neu ausgewählten Tarif" />
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
   <Button variant="contained" color="primary" onClick={handleKuendigung}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default,
                    float: "right",
                    mt: "10px"
                }} >
                    Vertrag wechseln    
                </Button>
                </Box>
    </Box>
    
}
   
   <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Wechselanfrage erfolgreich gestellt!" navigationGoal="/haushalte"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Antrag fehlgeschlagen"/>
    <SuccessModal open={conflictModalIsOpen} handleClose={() => setConflictModalIsOpen(false)}
    text="Vertrag wurde bereits gewechselt oder gekündigt!" navigationGoal="/haushalte"/>
        </Box>
    )
}

export default HaushalteVertragWechselnDetail;