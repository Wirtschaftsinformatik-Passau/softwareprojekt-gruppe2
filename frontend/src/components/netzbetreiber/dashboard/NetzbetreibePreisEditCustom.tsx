import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import {MenuItem, Select, FormControl, InputLabel, FormHelperText} from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import useMediaQuery from "@mui/material/useMediaQuery";
import SuccessModal from "../../utility/SuccessModal";
import {IUser, User, Nutzerrolle, UserDropDownOption} from "../../../entitities/user"
import axios from "axios";
import { Iadresse, Adresse } from "../../../entitities/adress";
import CircularProgress from '@mui/material/CircularProgress';
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";


export interface IPreis {
    bezugspreis_kwh: number;
    einspeisung_kwh: number;
}

export class Preis implements IPreis {
    bezugspreis_kwh: number;
    einspeisung_kwh: number;
    constructor(bezugspreis_kwh: number, einspeisung_kwh: number) {
        this.bezugspreis_kwh = bezugspreis_kwh;
        this.einspeisung_kwh = einspeisung_kwh;
    }
}




const NetzbetreiberTarifEdit = ({}) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [initialValues, setInitialValues] = React.useState({
        bezugspreis: "",
        einspeisepreis: "",
    })
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = React.useState(true);
    const { priceID } = useParams();  

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      axios.get(addSuffixToBackendURL("netzbetreiber/preisstrukturen/"+priceID), {headers: {Authorization: `Bearer ${token}`}})
        .then(response => {
            setInitialValues({
            bezugspreis: response.data.bezugspreis_kwh,
            einspeisepreis: response.data.einspeisung_kwh,
          });
          setIsLoading(false);
          console.log("Initial Values:", initialValues)
        })
        .catch(error => {
          console.log(error)
          setIsLoading(false);
        });
    }, []);
 
    const createPreis = (values: { tarifName: string; preisKwh: any; grundgebuehr: any; laufzeit: any; spezielleKonditionen: string; }, {setSubmitting}: any) => {

      const token = localStorage.getItem("accessToken");
      const preis = new Preis(Number(values.bezugspreis), Number(values.einspeisepreis))
      axios.put(addSuffixToBackendURL("netzbetreiber/preisstrukturen/" + priceID), preis, {headers: {Authorization: `Bearer ${token}`}})
          .then((response) => {
            if (response.status === 200) {
              setSuccessModalIsOpen(true)
              console.log("Preis erfolgreich gespeichert")
            } else {
              setFailModalIsOpen(true)
              console.log("Preis konnte nicht gespeichert werden")
            }
          
          })
          .catch((error) => {
              if (error.response && error.response.status === 422) {
                  console.log("Server Response on Error 422:", error.response.data);
              } else if (error.response && error.response.status === 401 || error.response.status === 403) {
                navigate("/login")
              } 
              else {
                console.log("Server Error:", error.message);
              }
          })
          .finally(() => {
              setSubmitting(false);
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
      <Header title="Preis bearbeiten" subtitle="Bearbeite den Preis mit allen nötigen Daten"/>
      {!isLoading &&(
      <Formik
        onSubmit={createPreis}
        initialValues={initialValues}
        validationSchema={checkoutSchema}
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
                "& > div": "span 4" ,
              }}
            >
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Bezugspreis"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.bezugspreis}
                name="bezugspreis"
                error={!!touched.bezugspreis && !!errors.bezugspreis}
                helperText={touched.bezugspreis && errors.bezugspreis}
                InputLabelProps={{
                  style: { color: touched.bezugspreis && errors.bezugspreis ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.bezugspreis && errors.bezugspreis ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.bezugspreis && errors.bezugspreis ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
               <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Einspeisepreis"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.einspeisepreis}
                name="einspeisepreis"
                error={!!touched.einspeisepreis && !!errors.einspeisepreis}
                helperText={touched.einspeisepreis && errors.einspeisepreis}
                InputLabelProps={{
                  style: { color: touched.einspeisepreis && errors.einspeisepreis ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.einspeisepreis && errors.einspeisepreis ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.einspeisepreis && errors.einspeisepreis ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              
            <Box display="flex" justifyContent="space-between" mt="20px" gridColumn= "span 4">
            <Button sx={{background: colors.grey[300],  color: theme.palette.background.default}} variant="contained"
            onClick={() => navigate("/netzbetreiber/priceEdit")}
            >
                Abbrechen
              </Button>
              <Button type="submit" sx={{background: colors.color1[400],  color: theme.palette.background.default}} variant="contained">
                Tarif erstellen
              </Button>
            </Box>
            </Box>
          </form>
        )}
        
      </Formik>
      )}

            
    <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Preis erfolgreich erstellt!" navigationGoal="/netzbetreiber"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Preis konnte nicht bearbeitet werden"/>
    </Box>
  
)}

      

    
const checkoutSchema = yup.object({
    bezugspreis: yup.number().typeError("Muss eine Zahl sein").test('input1-or-input2', 'Bitte Bezugspreis oder Einspeisepreis oder beide angeben', function(value) {
        const { einspeisepreis } = this.parent;
        return value || einspeisepreis}),
    einspeisepreis: yup.number().typeError("Muss eine Zahl sein").test('input1-or-input2', 'Bitte Bezugspreis oder Einspeisepreis oder beide angeben', function(value) {
        const { bezugspreis } = this.parent;
        return value || bezugspreis})})



export default NetzbetreiberTarifEdit;