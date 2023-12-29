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


interface IAntrag {
    "anlage_id": string,
    "haushalt_id": string | null,
    "solarteur_id": string | null,
    "modultyp": string  | null,
    "kapazitaet": number | null,
    "installationsflaeche": number | null,
    "installationsdatum": string | null,
    "modulanordnung": string | null,
    "kabelwegfuehrung": string | null,
    "montagesystem": string | null,
    "schattenanalyse": string | null,
    "wechselrichterposition": string | null,
    "installationsplan": string | null,
    "prozess_status": string,
    "nvpruefung_status": boolean | null

}

const NetzbetreiberEinspeisungenZusage = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const {isLoading, setIsLoading} = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [modalText, setModalText] = React.useState<string>("Einspeisezusage fehlgeschlagen")
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const {anlageID} = useParams();
    const [antrag, setAntrag] = React.useState<IAntrag>({
        "anlage_id": "",
    "haushalt_id": "",
    "solarteur_id": "",
    "modultyp": "",
    "kapazitaet": "",
    "installationsflaeche": "",
    "installationsdatum": "",
    "modulanordnung": "",
    "kabelwegfuehrung": "",
    "montagesystem": "",
    "schattenanalyse": "",
    "wechselrichterposition": "",
    "installationsplan": "",
    "prozess_status": "",
    "nvpruefung_status": ""
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


    //TODO: Add nvpruefung status to antrag   # wenn nv pruedung false kommt 400 zurück

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
            if (err.response.status === 403 || err.response.status === 401) {
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

    const handlePruefung = () => {
        const token = localStorage.getItem("accessToken");
        axios.put(addSuffixToBackendURL(`netzbetreiber/nvpruefung/${anlageID}`), {}, {headers: { Authorization: `Bearer ${token}` }})
        .then((res) => {
            console.log("success")
            setSuccessModalIsOpen(true)
        })
        .catch((err) => {
            if (err.response.status === 403 || err.response.status === 401) {
                console.log("Unauthorized  oder kein Netzbetreiber", err.response.data)
                navigate("/login")
              }
              else if (err.response.status === 400 || err.response.status === 501) {
                setModalText(err.response.data.detail)
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
                <Button variant="contained" color="primary" onClick={handlePruefung}
                 sx = {{
                    backgroundColor: `${colors.color2[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    NV Pruefung    
                </Button>
                {antrag.nvpruefung_status != null ||  antrag.nvpruefung_status == false &&(
                    <>
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
                </>
                )
}
            </Box>

    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
    {Object.entries(antrag).map(([key, value]) => {
        return ( key == "installationsplan" ? undefined :
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
    text={modalText}/>
        </Box>
    )
}

export default NetzbetreiberEinspeisungenZusage;