import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import ChangeCircleIcon from '@mui/icons-material/ChangeCircle';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import CircularProgress from '@mui/material/CircularProgress';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";

export interface Vertrag {
    "vorname": string,
    "nachname": string,
    "email": string,
    "vertrag_id": number,
    "netzbetreiber_id": number,
    "tarif_id": number,
    "beginn_datum": string,
    "end_datum": string,
    "jahresabschlag": number,
    "tarifname": string,
    "preis_kwh": number,
    "vertragstatus": boolean,
    "grundgebuehr": number,
    "laufzeit": 0,
    "spezielle_konditionen": string,
}



const VertragDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const {vertragID} = useParams();
    const [vertrag, setVertrag] = React.useState<Vertrag>({
            "vorname": "",
            "nachname": "",
            "email": "",
            "vertrag_id": 0,
            "netzbetreiber_id": 0,
            "tarif_id": 0,
            "beginn_datum": "",
            "end_datum": "",
            "jahresabschlag": 0,
            "tarifname": "",
            "preis_kwh": 0,
            "grundgebuehr": 0,
            "laufzeit": 0,
            "spezielle_konditionen": "",
            "vertragstatus": false,
                
    })

    const keyMapping = {
        "vorname": "Vorname Netzbetreiber",
        "nachname": "Nachname Netzbertreiber",
        "email": "E-Mail Netzbetreiber",
        "vertrag_id": "Vertrag ID",
        "netzbetreiber_id": "Netzbetreiber ID",
        "tarif_id": "Tarif ID",
        "beginn_datum": "Beginn Datum",
        "end_datum": "End Datum",
        "jahresabschlag": "Jahresabschlag in Euro",
        "tarifname": "Tarifname",
        "preis_kwh": "Preis pro kWh",
        "grundgebuehr": "Grundgebühr",
        "laufzeit": "Laufzeit in Jahren",
        "spezielle_konditionen": "Spezielle Konditionen",
        "vertragstatus": "Gekündigt"
    }

    const kuendigungsMapping = {
        true: "Nein",
        false: "Ja"
    }

    const navigate = useNavigate();

    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setVertrag, "haushalte/vertraege/"+vertragID , 
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []
    )

    const handleKuendigung = () => {
        const token = localStorage.getItem("accessToken");
        axios.put(addSuffixToBackendURL(`haushalte/vertrag-deaktivieren/${vertragID}`), {}, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }).then((response) => {
            setSuccessModalIsOpen(true);
        }).catch((error) => {
            setFailModalIsOpen(true);
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
            <Header title={"Detailübersicht Vertrag "+ vertragID}
             subtitle="Detaillierte Übersicht über abgeschlossenen Vertrag"/>
            <Box display={"flex"} justifyContent={"space-evenly"}>
            <Button variant="contained" color="primary" onClick={() => {navigate(-1)}}
                 sx = {{
                    backgroundColor: `${colors.grey[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Abbrechen    
                </Button>
                <Button variant="contained" color="primary" 
                onClick={() => navigate(`/haushalte/vertragChangeOverview/${vertragID}`)}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    <ChangeCircleIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                    Vertrag wechseln    
                </Button>
                <Button variant="contained" color="primary" onClick={handleKuendigung}
                sx = {{
                    backgroundColor: `${colors.color5[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    <DeleteForeverIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                    Vertrag kündigen    
                </Button>

            </Box>
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
    {Object.entries(vertrag).map(([key, value]) => {
        return (
            <Box gridColumn={(key === "spezielle_konditionen") ? "span 4" : "span 2"} mt={2} ml={1}>
            <TextField
            fullWidth
            variant="outlined"
            type="text"
            label={keyMapping[key]}
            name={key}
            value={key == "vertragstatus"? kuendigungsMapping[value] : value}
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
    text="Vertrag erfolgreich gekündigt!" navigationGoal="/haushalte"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Antrag fehlgeschlagen"/>
        </Box>
    )
}

export default VertragDetail;