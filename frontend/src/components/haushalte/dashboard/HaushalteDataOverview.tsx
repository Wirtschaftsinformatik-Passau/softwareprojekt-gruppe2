import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import CircularProgress from '@mui/material/CircularProgress'
import { IHaushaltData, Isolierungsqualitaet, Orientierung } from "../../../entitities/haushalt";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { IUserFull } from "./HaushaltSmartMeterUpload";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";



const HaushalteData = ({}) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [dashbaordModalIsOpen, setDashbaordModalIsOpen] = React.useState(false);
    const [currentUser, setCurrentUser] = React.useState<IUserFull | null>(null);
    const [dataExists, setDataExists] = React.useState<boolean>(false);
    const [headerText, setHeaderText] = React.useState<string>("Daten bearbeiten");
    const [initialValues, setInitialValues] = React.useState<IHaushaltData>({
        anzahl_bewohner: "",
        heizungsart: "",
        baujahr: "",
        wohnflaeche: "",
        isolierungsqualitaet: "",
        ausrichtung_dach: "",
        dachflaeche: "",
        energieeffizienzklasse: "",
  })
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = React.useState(true);

    const keyMapping = {
      anzahl_bewohner: "Anzahl Bewohner",
      heizungsart: "Heizungsart",
      baujahr: "Baujahr",
      wohnflaeche: "Wohnfläche",
      isolierungsqualitaet: "Isolierungsqualität",
      ausrichtung_dach: "Ausrichtung des Daches",
      dachflaeche: "Dachfläche",
      energieeffizienzklasse: "Energieeffizienzklasse",
    }
    

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      axios.get(addSuffixToBackendURL("users/current/single"), {headers: {Authorization: `Bearer ${token}`}})
      .then(firstResponse => {
        setCurrentUser(firstResponse.data);
        axios.get(addSuffixToBackendURL("haushalte/haushalt-daten/"+firstResponse.data.user_id), {headers: {Authorization: `Bearer ${token}`}})
        .then(response => {
          setInitialValues({
            anzahl_bewohner: response.data.anzahl_bewohner,
            heizungsart: response.data.heizungsart,
            baujahr: response.data.baujahr,
            wohnflaeche: response.data.wohnflaeche,
            isolierungsqualitaet: response.data.isolierungsqualitaet,
            ausrichtung_dach: response.data.ausrichtung_dach,
            dachflaeche: response.data.dachflaeche,
            energieeffizienzklasse: response.data.energieeffizienzklasse,
          });
          setIsLoading(false);
          setDataExists(true);
        })
        .catch(error => {
          if (error.response && error.response.status === 404) {
            setHeaderText("Haushaltsdaten müssen noch angelegt werden")
            setIsLoading(false);
            }
          else if (error.response && error.response.status === 401 || error.response.status === 403) {
            navigate("/login")
          }
          else if (error.response && error.response.status === 412) {
            setHeaderText("Dringendes Anlegen der Daten erforderlich, da Solarteur Datenanfrage gestellt hat")
            setIsLoading(false);
          }
        });
      })
    }, []);
 
    const updateData = (values: IHaushaltData, {setSubmitting}: any) => {

      const token = localStorage.getItem("accessToken");
      const haushalt = {anzahl_bewohner: values.anzahl_bewohner,
                        heizungsart: values.heizungsart,
                        baujahr: values.baujahr,
                        wohnflaeche: values.wohnflaeche,
                        isolierungsqualitaet: values.isolierungsqualitaet,
                        ausrichtung_dach: values.ausrichtung_dach,
                        dachflaeche: values.dachflaeche,
                        energieeffizienzklasse: values.energieeffizienzklasse,}

        if (dataExists) {

        axios.put(addSuffixToBackendURL("haushalte/" + currentUser?.user_id), haushalt, {headers: {Authorization: `Bearer ${token}`}})
            .then((response) => {
                if (response.status === 200) {
                setSuccessModalIsOpen(true)
                } else {
                setFailModalIsOpen(true)
                console.log("Daten konnten nicht gespeichert werden")
                }
            
            })
            .catch((error) => {
              console.log("catching")
                if (error.response && error.response.status === 422) {
                    console.log("Server Response on Error 422:", error.response.data);
                }
                else if (error.response && error.response.status === 401 || error.response.status === 403) {
                    navigate("/login")
                } 
                else if (error.response && error.response.status === 412) {
                  setDashbaordModalIsOpen(true)
                  setIsLoading(false);
                }else {
                setFailModalIsOpen(true)
                }
            })
            .finally(() => {
                setSubmitting(false);
            })
        }
        else {
            axios.post(addSuffixToBackendURL("haushalte/datenfreigabe"), haushalt, {headers: {Authorization: `Bearer ${token}`}})
            .then((response) => {
                if (response.status === 201) {
                setSuccessModalIsOpen(true)
                } else {
                setFailModalIsOpen(true)
                console.log("Daten konnten nicht gespeichert werden")
                }
            
            })
            .catch((error) => {
              console.log("catching")
                if (error.response && error.response.status === 422) {
                    console.log("Server Response on Error 422:", error.response.data);
                }
                else if (error.response && error.response.status === 401 || error.response.status === 403) {
                    navigate("/login")
                } 
                else if (error.response && error.response.status === 412) {
                  setDashbaordModalIsOpen(true)
                  setIsLoading(false);
                }else {
                setFailModalIsOpen(true)
                }
            })
            .finally(() => {
                setSubmitting(false);
            })
        }
  
  
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
      <Header title="Haushaltsdaten" subtitle={headerText}/>
      <Formik
        onSubmit={updateData}
        initialValues={initialValues}
        validationSchema={checkoutSchemaHaushalt}
        style={{
          display:"flex",
          flexDirection:"column",
          justifyContent:"space-between"
        }}
      >
        {({
          values,
          errors,
          touched,
          handleBlur,
          handleChange,
          handleSubmit,
        }) => (
          <form onSubmit={handleSubmit}>
            <Box
              display="grid"
              gap="30px"
              gridTemplateColumns="repeat(4, minmax(0, 1fr))"
              sx={{
                "& > div": {gridColumn: "span 2"} 
              }}
            >
               {Object.entries(initialValues).map(([key, value]) => {
                return (
                  <TextField
                    fullWidth
                    variant="outlined"
                    type="text"
                    label={keyMapping[key]}
                    onBlur={handleBlur}
                    onChange={handleChange}
                    value={values[key]}
                    name={key}
                    error={!!touched[key] && !!errors[key]}
                    helperText={touched[key] && errors[key]}
                    InputLabelProps={{
                      style: { color: touched[key] && errors[key] ? 'red' : `${colors.color1[500]}` }
                  }}
                  sx={{
                      gridColumn: "span 2",
                      '& .MuiInputBase-input': { 
                          color: touched[key] && errors[key] ? 'red' : `${colors.color1[500]} !important`,
                      },
                      '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: touched[key] && errors[key] ? 'red' : `${colors.color1[500]} !important`,
                      },
                  }}
                  />
                )
               })}
              
              <Box sx={{display: "flex", justifyContent: "space-between", gridColumn: "span 12" ,  width:"200%"}}>
              <Button variant="contained"  sx= {{
                backgroundColor: `${colors.grey[500]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px",
            }}  onClick= {() => navigate(-1)}>
                Abbrechen
            </Button>
            <Button variant="contained" sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px"
            }}  type="submit">
                Daten speichern
            </Button>
            </Box>
            </Box>
          </form>
        )}
        
      </Formik>

            
    <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Haushaltsdaten erfolgreich gespeichert!" navigationGoal="/haushalte/"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Es gabe einen Fehler bei der Speicherung"/>
    <SuccessModal open={dashbaordModalIsOpen} handleClose={() => setDashbaordModalIsOpen(false)}
    text="Dashboard Daten müssen erst noch hochgeladen werden" navigationGoal="/haushalte/pvuploadOverview"/>
    </Box>
  
)}

    
export const checkoutSchemaHaushalt = yup.object({
    anzahl_bewohner: yup.number().typeError("Nur Zahlen zugelassen").required("Anzahl Bewohner ist erforderlich"),
    heizungsart: yup.string().required("Heizungsart ist erforderlich"),
    baujahr: yup.number().typeError("Nur Zahlen zugelassen").required("Baujahr ist erforderlich"),
    wohnflaeche: yup.number().typeError("Nur Zahlen zugelassen").required("Wohnfläche ist erforderlich"),
    isolierungsqualitaet: yup.string().oneOf([Isolierungsqualitaet.hoch, Isolierungsqualitaet.mittel, Isolierungsqualitaet.niedrig]).required("Isolierungsqualität ist erforderlich"),
    ausrichtung_dach: yup.string().oneOf([Orientierung.Nord, Orientierung.Nordost, Orientierung.Nordwest, Orientierung.Sued, Orientierung.Suedost, Orientierung.Suedwest]).required("Ausrichtung des Daches ist erforderlich"),
    dachflaeche: yup.number().typeError("Nur Zahlen zugelassen").required("Dachfläche ist erforderlich"),
    energieeffizienzklasse: yup.string().required("Energieeffizienzklasse ist erforderlich"),
});

export default HaushalteData;