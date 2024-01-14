import React, { useEffect } from "react";
import { Box, Button, TextField, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams, useSearchParams} from "react-router-dom";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import CheckIcon from '@mui/icons-material/Check';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import NetworkCheckIcon from '@mui/icons-material/NetworkCheck';
import CircularProgress from '@mui/material/CircularProgress';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import Header from "../../utility/Header";
import { NetzbetreiberDetailPV, ProzessStatus } from "../../../entitities/pv";


const NetzbertreiberEinspeisungenDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [nvPruefungModalIsOpen, setNvPruefungModalIsOpen] = React.useState<boolean>(false);
    const [nvPruefungFailModalIsOpen, setNvPruefungFailModalIsOpen] = React.useState<boolean>(false);
    const [einspeisezusageModalIsOpen, setEinspeisezusageModalIsOpen] = React.useState<boolean>(false);
    const [einspeisezusageFailModalIsOpen, setEinspeisezusageFailModalIsOpen] = React.useState<boolean>(false);
    const [nvpruefungSuccess, setNvPruefungSuccess] = React.useState<boolean>(false)
    const [searchParams, setSearchParams] = useSearchParams();
    const status = searchParams.get("prozess_status");
    const planErstellt = status === ProzessStatus.PlanErstellt ? true : false;
    const {anlageID} = useParams();
    const [antrag, setAntrag] = React.useState<NetzbetreiberDetailPV>({
        anlage_id: "",
        haushalt_id: "",
        solarteur_id: "",
        modultyp: "",
        kapazitaet: "",
        installationsflaeche: "",
        installationsdatum: "",
        modulanordnung: "",
        kabelwegfuehrung: "",
        montagesystem: "",
        schattenanalyse: "",
        wechselrichterposition: "",
        installationsplan: "",
        prozess_status: "",
        nvpruefung_status: "",
        vorname: "",
        nachname: "",
        strasse: "",
        hausnr: "",
        plz: "",
        stadt: ""
    })
  

   const keyMappingEinspeisung = {
    anlage_id: "Anlage ID",
    haushalt_id: "Haushalt ID",
    solarteur_id: "Solarteur ID",
    modultyp: "Modultyp",
    kapazitaet: "Kapazitaet",
    installationsflaeche: "Installationsflaeche",
    installationsdatum: "Installationsdatum",
    modulanordnung: "Modulanordnung",
    kabelwegfuehrung: "Kabelwegfuehrung",
    montagesystem: "Montagesystem",
    schattenanalyse: "Schattenanalyse",
    wechselrichterposition: "Wechselrichterposition",
    installationsplan: "Installationsplan",
    prozess_status: "Prozess Status",
    nvpruefung_status: "NV Prüfung Status",
    vorname: "Vorname",
    nachname: "Nachname",
    strasse: "Strasse",
    hausnr: "Hausnummer",
    plz: "PLZ",
    stadt: "Stadt"
   }


    const navigate = useNavigate();

    useEffect(() =>{
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setAntrag, "netzbetreiber/einspeisezusagen/" + anlageID,
        navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
    },[])

    const pruefungsButton = () => {
        const token = localStorage.getItem("accessToken");
        axios.put(addSuffixToBackendURL("netzbetreiber/nvpruefung/" + anlageID), {}, {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            if (response.status == 202 && response.data.nvpruefung_status){
                setNvPruefungModalIsOpen(true)
                setNvPruefungSuccess(true)
            }
            else {
                setNvPruefungFailModalIsOpen(true)
            }
        })
        .catch((error) => {
            if (error.response.status === 403 || error.response.status === 401) {
                navigate("/login");
            }
            setNvPruefungFailModalIsOpen(true);
            console.log(error);
        })
    }

    const annehmenButton = () => {
        const token = localStorage.getItem("accessToken");
        axios.put(addSuffixToBackendURL("netzbetreiber/einspeisezusage/" + anlageID), {}, {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            setEinspeisezusageModalIsOpen(true);
        })
        .catch((error) => {
            if (error.response.status === 403 || error.response.status === 401) {
                navigate("/login");
            }
            else {
                setEinspeisezusageFailModalIsOpen(true);
            }
            console.log(error);
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
            <Header title={"Detailübersicht Anfrage "+ anlageID}
             subtitle="Detaillierte Übersicht über Anfrage"/>
            
        <Box mt="30px" display={"grid"} columnGap={"5%"} gridTemplateColumns={"repeat(4, minmax(0, 1fr))"}>
        <Box display={"flex"} justifyContent={"space-evenly"} gridColumn={"span 4"}>
            <Button variant="contained" color="primary" onClick={() => {navigate(-1)}}
                 sx = {{
                    backgroundColor: `${colors.grey[400]} !important`,
                    color: theme.palette.background.default
                }}>
                    Abbrechen    
                </Button>
                {planErstellt &&
                 nvpruefungSuccess ?
                <>
                <Button variant="contained" color="primary" 
                sx = {{
                    backgroundColor: `${colors.color5[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    <DeleteForeverIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                        Einspeisezusage ablehnen
                </Button>
                <Button variant="contained" color="primary" 
                onClick= {annehmenButton}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    <CheckIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                    Einspeisezusage erteilen    
                </Button>
                </> :
                    <>
                <Button variant="contained" color="primary" 
                onClick={() => pruefungsButton()}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    <NetworkCheckIcon sx={{
                        marginRight: "6px",
                        marginBottom: "1px"
                    
                    }}/>
                    Netzverträglichkeitsprüfung    
                </Button>
                </>
                
}

            </Box>
             <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"} gridColumn={"span 4"}>
            {Object.entries(antrag).map(([key, value], index) => {
                return ( 
                    key == "haushalt_id" || key == "anlage_id" || key == "installationsplan" ? undefined :
                    <Box key={index} gridColumn={(key === "spezielle_konditionen") ? "span 4" : "span 2"} mt={2} ml={1}>
                        <TextField
                            fullWidth
                            variant="outlined"
                            type="text"
                            label={keyMappingEinspeisung[key]}
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
                            }}
                        />
                    </Box>
                );
            })}
        </Box>   
   <SuccessModal open={nvPruefungModalIsOpen} handleClose={() => setNvPruefungModalIsOpen(false)} 
    text="Netzverträglichkeitsprüfung erfolgreich durchgeführt!"/>
    <SuccessModal open={nvPruefungFailModalIsOpen} handleClose={() => setNvPruefungFailModalIsOpen(false)} 
    text="Netzverträglichkeitsprüfung fehlgeschlagen"/>   
    <SuccessModal open={einspeisezusageModalIsOpen} handleClose={() => setEinspeisezusageModalIsOpen(false)} 
    text="Einspeisezusage erfolgreich erteilt!" navigationGoal="/netzbetreiber"/>
    <SuccessModal open={einspeisezusageFailModalIsOpen} handleClose={() => setEinspeisezusageFailModalIsOpen(false)} 
    text="Einspeisezusage fehlgeschlagen"/>   

        </Box>
        </Box>
    )
}

export default NetzbertreiberEinspeisungenDetail;
