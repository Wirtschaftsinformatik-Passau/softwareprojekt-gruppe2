import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import axios from "axios";
import CircularProgress from '@mui/material/CircularProgress';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { Angebot } from "../../../entitities/pv";
import { dateFormater } from "../../../utils/dateUtils";


const HaushalteAngebotDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const [ablehnenModalIsOpen, setAblehnenModalIsOpen] = React.useState<boolean>(false);
    const [ablehnenFailModalIsOpen, setAblehnenFailModalIsOpen] = React.useState<boolean>(false);
    const {anlageID} = useParams();
    const [angebote , setAngebote] = React.useState<Angebot[]>([{
        angebot_id: 0,
        modulanordnung: "",
        modultyp: "",
        kapazitaet: "",
        installationsflaeche: "",
        kosten: "",
        angebotsstatus:  "",
        created_at: "",
    }])

    const keyMapping = {
        angebot_id: "Angebot ID",
        modulanordnung: "Modulanordnung",
        modultyp: "Modultyp",
        kapazitaet: "Kapazität",
        installationsflaeche: "Installationsfläche",
        kosten: "Kosten",
        angebotsstatus: "Angebotsstatus",
        created_at: "Erstellt am",
    }

    const navigate = useNavigate();

    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setAngebote, "haushalte/angebote/"+anlageID , 
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []
    )

   const handleAnnehmen = () => {
        const token = localStorage.getItem("accessToken");
        const url = addSuffixToBackendURL("haushalte/angebot-akzeptieren/"+anlageID);
        axios.put(url, {}, {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            setSuccessModalIsOpen(true);
        })
        .catch((error) => {
            setFailModalIsOpen(true);
        })
    }

    const handleAblehnen = () => {
        const token = localStorage.getItem("accessToken");
        const url = addSuffixToBackendURL("haushalte/angebot-ablehnen/"+anlageID);
        axios.put(url, {}, {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            setAblehnenModalIsOpen(true);
        })
        .catch((error) => {
            setAblehnenFailModalIsOpen(true);
        })
    }


    const kontaktAufnahme = () => {
        const token = localStorage.getItem("accessToken");
        const url = addSuffixToBackendURL("haushalte/kontaktaufnahme-energieberatenden?anlage_id=" + anlageID);
        axios.post(url, {}, {headers: {Authorization: `Bearer ${token}`}})
        .then((res) => {
            console.log("Kontaktaufnahme erfolgreich")
        })
        .catch((error) => {
            console.log("Kontaktaufnahme nicht erfolgreich")
        })
    }

    // TODO: Angebot daten anzeigen von Solarteuer

    if (isLoading) {
        return (
          <Box display="flex" justifyContent="center" alignItems="center" height="300px">
            <CircularProgress />
          </Box>
        );
      }

      
    return (
        <Box>
        {angebote.map((angebot) => {
            return (
        <Box m="20px">
            <Header title={"Detailübersicht Angebot "+ angebot.angebot_id}
             subtitle="Detaillierte Übersicht über erhaltenes Angebot"/>
            <Box display={"flex"} justifyContent={"space-evenly"}>
            <Button variant="contained" color="primary" onClick={() => {navigate(-1)}}
                 sx = {{
                    backgroundColor: `${colors.grey[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Abbrechen    
                </Button>
                <Button variant="contained" color="primary" onClick={handleAblehnen}
                sx = {{
                    backgroundColor: `${colors.color5[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    <CloseIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                    Angebot ablehnen    
                </Button>
                <Button variant="contained" color="primary" onClick={() => {
                    handleAnnehmen(angebot.angebot_id)
                    kontaktAufnahme()}}
                sx = {{
                    backgroundColor: `${colors.color1[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    <CheckIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                    Angebot annehmen    
                </Button>

            </Box>
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
    {Object.entries(angebot).map(([key, value]) => {
        return  ((key == "angebot_id") || (key == "angebotsstatus") ? null :
            <Box gridColumn={(key === "spezielle_konditionen") ? "span 4" : "span 2"} mt={2} ml={1}>
            <TextField
            fullWidth
            variant="outlined"
            type="text"
            label={keyMapping[key]}
            name={key}
            value={key == "created_at" ? dateFormater(value) : value}
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
        </Box>
        )
        }
        )
        }
        
   <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Angebot erfolgreich angenommen!" navigationGoal="/haushalte"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Angebot konnte nicht angenommen werden!"/>
    <SuccessModal open={ablehnenModalIsOpen} handleClose={() => setAblehnenModalIsOpen(false)}
    text="Angebot erfolgreich abgelehnt!" navigationGoal="/haushalte"/>
    <SuccessModal open={ablehnenFailModalIsOpen} handleClose={() => setAblehnenFailModalIsOpen(false)}
    text="Angebot konnte nicht abgelehnt werden!"/>
    
        </Box>
    )
}

export default HaushalteAngebotDetail;