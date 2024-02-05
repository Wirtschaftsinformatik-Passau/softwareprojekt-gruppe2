import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams, useSearchParams} from "react-router-dom";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import ChangeCircleIcon from '@mui/icons-material/ChangeCircle';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import CircularProgress from '@mui/material/CircularProgress';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { IHaushaltData } from "../../../entitities/haushalt";
import { Angebot, PVAngebotCreate, ProzessStatus } from "../../../entitities/pv";
import Header from "../../utility/Header";
import { EnergieausweisCreate, SolarteurResponse, EnergieeffizienzmassnahmenCreate, MassnahmeTyp, } from "../../../entitities/pv";
import EnergieberatendeAusweisErstellen from "./EnergieberatendeAusweisErstellen";
import EnergieberaterAbnahme from "./EnergieberaterAbnahme";

export interface EnergieberatendeResponseExtended extends SolarteurResponse {
    haushalt_id: number
    energieausweis_id: number
}

const EnergieberatendeAnfragenDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const [datenfreigabe, setDatenfreigabe] = React.useState<boolean>(false);
    const [aufFreigabeWarten, setAufFreigabeWarten] = React.useState<boolean>(false);
    const [initialFailModelIsOpen, setInitialFailModalIsOpen] = React.useState<boolean>(false);
    const [planSuccessModalIsOpen, setPlanSuccessModalIsOpen] = React.useState<boolean>(false);
    const [planFailModalIsOpen, setPlanFailModalIsOpen] = React.useState<boolean>(false);
    const [searchParams, setSearchParams] = useSearchParams();
    const status = searchParams.get("status");
    const ausweisErstellen = status === ProzessStatus.AusweisAngefordert.valueOf() ? true : false;
    const planErstellen = status === ProzessStatus.AusweisErstellt.valueOf() ? true : false;
    const abnehmen = status === ProzessStatus.Genehmigt.valueOf() ? true : false;

    const {anlageID} = useParams();
    const navigate = useNavigate();

    const ausweis: EnergieausweisCreate = {
        energieeffizienzklasse: "",
        verbrauchskennwerte: "",
        gueltigkeit: "",
    }
   

    const massnahmen: EnergieeffizienzmassnahmenCreate = {
        massnahmetyp: "",
        einsparpotenzial: "",
        kosten: "",
    }
        

    const [antrag, setAntrag] = React.useState<EnergieberatendeResponseExtended>({
        anlage_id: 0,
        haushalt_id: 0,
        prozess_status: "",
        vorname: "",
        nachname: "",
        email: "",
        strasse: "",
        hausnummer: 0,
        plz: 0,
        stadt: "",
        energieausweis_id: 0,
    })  

    const [hauhalt, setHaushalt] = React.useState<IHaushaltData>({
           anzahl_bewohner: "",
              heizungsart: "",
              baujahr: "",
              wohnflaeche: "",
              isolierungsqualitaet: "",
              ausrichtung_dach: "",
              dachflaeche: "",
              energieeffizienzklasse: "",
    })

   const keyMappingHaushalt = {
        anzahl_bewohner: "Anzahl Bewohner",
        heizungsart: "Heizungsart",
        baujahr: "Baujahr",
        wohnflaeche: "Wohnfläche",
        isolierungsqualitaet: "Isolierungsqualität",
        ausrichtung_dach: "Ausrichtung Dach",
        dachflaeche: "Dachfläche",
        energieeffizienzklasse: "Energieeffizienzklasse",
    }

    const keyMappingAntrag = {
        anlage_id: "Anlage ID",
        hauhalt_id: "Haushalt ID",
        prozess_status: "Prozess Status",
        vorname: "Vorname",
        nachname: "Nachname",
        email: "Email",
        strasse: "Straße",
        hausnummer: "Hausnummer",
        plz: "PLZ",
        stadt: "Stadt",
    }



    // fetch anfrage and haushalt data and render the text fiedlds
    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("energieberatende/anfragen/" + anlageID), {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            setAntrag(response.data);
            console.log(response.data)
            axios.get(addSuffixToBackendURL("haushalte/haushalt-daten/" + response.data.haushalt_id), {headers: {Authorization: `Bearer ${token}`}})
            .then((response) => {
                setHaushalt(response.data);
                setIsLoading(false);
            })
            .catch((error) => {
                if (error.response.status === 404) {
                    setDatenfreigabe(true);
                    setIsLoading(false);
                }
                if (error.response.status === 412) {
                    setAufFreigabeWarten(true);
                    setIsLoading(false);
                }
                else {
                    setInitialFailModalIsOpen(true);
                    setIsLoading(false);
                }
                console.log(error);
            })
        })
        .catch((error) => {
            if (error.response.status === 403 || error.response.status === 401) {
                navigate("/login");
            }
            console.log(error);
        })
    }, []
    )


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
            
            {datenfreigabe ? 
            <Box>
                <Box justifyContent={"center"} display={"flex"}>
                 <Typography variant="h5" color={colors.color1[400]} sx={{mb: 2}}>
                Haushaltsdaten wurden noch nicht freigegeben
                </Typography>
                </Box>
            <Box sx={{display: "flex", justifyContent: "center" , marginTop: "5px"}}>
            <Button variant="contained" sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px",
                width: "100%",
            }}  onClick={freigabeButton}>
                Haushaltsdaten anfragen
            </Button>
            </Box> 
            </Box>
            : aufFreigabeWarten ? 
            <Box display={"grid"} gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} justifyContent={"center"}>
                <Box gridColumn={"span 4"} justifyContent={"center"} display={"flex"}>
            <Typography variant="h5" color={colors.color1[400]} sx={{mb: 2}}>
                Datenfreigabe für Haushalt angefragt, aber noch ausstehend
                </Typography>
                </Box>
                <Box gridColumn={"span 4"}>
                <LinearProgress sx={{ bgcolor: colors.color1[400] }}/>
                </Box>
            </Box> 
            : abnehmen ?
                <>
            {<EnergieberaterAbnahme anlageID={Number(anlageID)} navigateFN={navigate} sucessModalSetter={setPlanSuccessModalIsOpen}
            failModalSetter={setPlanFailModalIsOpen} />}
                </>
      :
            
    <Box mt="30px" display={"grid"} columnGap={"5%"} gridTemplateColumns={"repeat(4, minmax(0, 1fr))"}>
         <Box  gridColumn={"span 2"}>
             <Header title={"Übersicht Antrag"} variant="h3"
             subtitle="Infomationen zum ausgewählten Antrag"/>
             </Box>
        <Box gridColumn={"span 2"}>
        <Header title={"Haushaltsdaten"} subtitle="Vom Haushalt angegebene Daten" variant="h3"/>
        </Box>
             <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"} gridColumn={"span 2"}>
            {Object.entries(antrag).map(([key, value], index) => {
                return ( 
                    key == "haushalt_id" || key == "anlage_id" || key == "energieausweis_id" ? undefined :
                    <Box key={index} gridColumn={(key === "spezielle_konditionen") ? "span 4" : "span 2"} mt={2} ml={1}>
                        <TextField
                            fullWidth
                            variant="outlined"
                            type="text"
                            label={keyMappingAntrag[key]}
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
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"} gridColumn={"span 2"}>
    {Object.entries(hauhalt).map(([key, value]) => {
        return (
            <Box gridColumn={(key === "spezielle_konditionen") ? "span 4" : "span 2"} mt={2} ml={1}>
            <TextField
            fullWidth
            variant="outlined"
            type="text"
            label={keyMappingHaushalt[key]}
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
   {ausweisErstellen ? <EnergieberatendeAusweisErstellen ausweis={ausweis} massnahmen={massnahmen} navigateFN={navigate} 
   sucessModalSetter={setSuccessModalIsOpen} failModalSetter={setFailModalIsOpen} energieausweisID={antrag.energieausweis_id}/>
      :
      <>
    {undefined}
        
        </>
}
   </Box>
   
}
   <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Energiesausweis erfolgreich erstellt!" navigationGoal="/energieberatende"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Energiesausweis konnte nicht erstellt werden"/>
    <SuccessModal open={planSuccessModalIsOpen} handleClose={() => setPlanSuccessModalIsOpen(false)}
    text="Anlage wurde erfolgreich abgenommen" navigationGoal="/energieberatende"/>
    <SuccessModal open={planFailModalIsOpen} handleClose={() => setPlanFailModalIsOpen(false)}
    text="Anlage konnte nicht abgenommen werden"/>
    

        </Box>
    )
}



export default EnergieberatendeAnfragenDetail;
