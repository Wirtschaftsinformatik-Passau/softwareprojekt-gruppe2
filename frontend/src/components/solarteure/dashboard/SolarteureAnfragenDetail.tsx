import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import ChangeCircleIcon from '@mui/icons-material/ChangeCircle';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import CircularProgress from '@mui/material/CircularProgress';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { IHaushaltData } from "../../../entitities/haushalt";
import { PVAngebotCreate } from "../../../entitities/pv";
import Header from "../../utility/Header";
import { Orientierung } from "../../../entitities/haushalt";



const AnfrageDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const [initialFailModelIsOpen, setInitialFailModalIsOpen] = React.useState<boolean>(false);
    const [conflictModalIsOpen, setConflictModalIsOpen] = React.useState<boolean>(false);
    const [datenfreigabe, setDatenfreigabe] = React.useState<boolean>(false);
    const [aufFreigabeWarten, setAufFreigabeWarten] = React.useState<boolean>(false);
    const {anlageID} = useParams();
    const [antrag, setAntrag] = React.useState<PVAngebotCreate>({
            anlage_id: "",
            modultyp: "",
            kapazitaet: "",
            installationsflaeche: "",
            modulanordnung: "",
            kosten: "",
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

    const kuendigungsMapping = {
        true: "Nein",
        false: "Ja"
    }

    const navigate = useNavigate();

    useEffect(() => {  
        const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("solarteure/anfragen/" + anlageID), {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            setAntrag(response.data);
            axios.get(addSuffixToBackendURL("haushalte/" + response.data.haushalt_id), {headers: {Authorization: `Bearer ${token}`}})
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
            {datenfreigabe ? <Box></Box> : aufFreigabeWarten ? <Box></Box> : 
            
            
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
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
}
   <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Vertrag erfolgreich gekündigt!" navigationGoal="/haushalte"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Antrag fehlgeschlagen"/>
    <SuccessModal open={conflictModalIsOpen} handleClose={() => setConflictModalIsOpen(false)}
    text="Vetrag wurde bereits gewechselt oder ist gekündigt!"/>
        </Box>
    )
}

const angebotSchema = yup.object({
    modultyp: yup.string().required("Modultyp ist erforderlich"),
    kapazitaet: yup.string().required("Kapazität ist erforderlich"),
    installationsflaeche: yup.string().required("Installationsfläche ist erforderlich"),
    modulanordnung: yup.string().oneOf(Object.values(Orientierung)).required("Modulanordnung ist erforderlich"),
    kosten: yup.string().required("Kosten sind erforderlich"),
})

export default AnfrageDetail;
