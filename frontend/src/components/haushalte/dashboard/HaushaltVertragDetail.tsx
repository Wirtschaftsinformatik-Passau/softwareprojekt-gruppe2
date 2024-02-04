import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams, useSearchParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import ChangeCircleIcon from '@mui/icons-material/ChangeCircle';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import CircularProgress from '@mui/material/CircularProgress';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { Vertrag } from "../../../entitities/vertrag";



const HaushalteVertragDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const [conflictModalIsOpen, setConflictModalIsOpen] = React.useState<boolean>(false);
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
            "vertragstatus": "",
                
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
        "vertragstatus": "Vertragstatus"
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
        axios.post(addSuffixToBackendURL(`haushalte/kuendigungsanfrage/${vertragID}`), {}, {
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
                onClick={() => navigate(`/haushalte/vertragChangeOverview/${vertragID}?oldTarifID=${vertrag.tarif_id}`)}
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
            value={(value === "Gekuendigt_Unbestaetigt") ? "Bestätigung ausstehend" : value}
            disabled
            
            InputLabelProps={{
              style: { color: `${colors.color1[500]}` },
          }}
          sx={{
              gridColumn: "span 2",
              '& .MuiInputBase-input': { 
                color: `${colors.color1[500]} !important`,
                background: value === "Gekuendigt_Unbestaetigt" ? colors.color4[400] :
                            value === "Laufend" ? colors.color3[400] :
                            value === "Gekuendigt" ? colors.color5[400] :
                            undefined 
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
    text="Kündigungsantrag erfolgreich gestellt!" navigationGoal="/haushalte"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Antrag fehlgeschlagen"/>
    <SuccessModal open={conflictModalIsOpen} handleClose={() => setConflictModalIsOpen(false)}
    text="Vetrag wurde bereits gewechselt oder ist gekündigt!"/>
        </Box>
    )
}

export default HaushalteVertragDetail;