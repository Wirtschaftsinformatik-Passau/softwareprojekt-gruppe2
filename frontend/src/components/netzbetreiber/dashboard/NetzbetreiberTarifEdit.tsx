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
import { ITarif, Tarif } from "../../../entitities/tarif";





const NetzbetreiberTarifEdit = ({}) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [deleteModalIsOpen, setDeleteModalIsOpen] = React.useState(false);
    const [deleteFailModalisOpen, setDeleteFailModalisOpen] = React.useState(false)
    const [overallFailModalIsOpen, setOverallFailModalIsOpen] = React.useState(false)
    const [initialValues, setInitialValues] = React.useState({
      tarifName: "",
      preisKwh: "",
      grundgebuehr: "",
      laufzeit: "",
      spezielleKonditionen: "",
  })
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = React.useState(true);
    const { tarifID } = useParams();  
    console.log("userId:", tarifID)

    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      axios.get(addSuffixToBackendURL("netzbetreiber/tarife/"+tarifID), {headers: {Authorization: `Bearer ${token}`}})
        .then(response => {
          setInitialValues({
            tarifName: response.data.tarifname,
            preisKwh: response.data.preis_kwh,
            grundgebuehr: response.data.grundgebuehr,
            laufzeit: response.data.laufzeit,
            spezielleKonditionen: response.data.spezielle_konditionen
          });
          console.log("Tarif:", initialValues)
          setIsLoading(false);
        })
        .catch(error => {
          console.log(error)
          setIsLoading(false);
        });
    }, []);


 
    const createTarif = (values: { tarifName: string; preisKwh: any; grundgebuehr: any; laufzeit: any; spezielleKonditionen: string; }, {setSubmitting}: any) => {

      const token = localStorage.getItem("accessToken");
      const tarif: ITarif = new Tarif(values.tarifName, Number(values.preisKwh), Number(values.grundgebuehr), Number(values.laufzeit), 
      values.spezielleKonditionen)
      console.log("tarif:", tarif )
      axios.put(addSuffixToBackendURL("netzbetreiber/tarife/" + tarifID), tarif, {headers: {Authorization: `Bearer ${token}`}})
          .then((response) => {
            if (response.status === 200) {
              setSuccessModalIsOpen(true)
              console.log("Tarif erfolgreich gespeichert")
            } else {
              setFailModalIsOpen(true)
              console.log("Tarif konnte nicht gespeichert werden")
            }
          
          })
          .catch((error) => {
              if (error.response && error.response.status === 422) {
                  console.log("Server Response on Error 422:", error.response.data);
              } else if (error.response && error.response.status === 401 || error.response.status === 403) {
                navigate("/login")
              } 
              else if (error.response && error.response.status === 409) {
                setFailModalIsOpen(true)
              } else {
                setOverallFailModalIsOpen(true)
              }
          })
          .finally(() => {
              setSubmitting(false);
          })
  }

  const deleteTarif = () => {
    const token = localStorage.getItem("accessToken");
    axios.delete(addSuffixToBackendURL("netzbetreiber/tarife/" + tarifID), {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
          if (response.status === 204) {
            setDeleteModalIsOpen(true)
            console.log("Tarif erfolgreich gelöscht")
          } else {
            setDeleteFailModalisOpen(true)
            console.log("Tarif konnte nicht gelöscht werden")
          }
        
        })
        .catch((error) => {
            if (error.response && error.response.status === 422) {
                console.log("Server Response on Error 422:", error.response.data);
            } else if (error.response && error.response.status === 401 || error.response.status === 403) {
              navigate("/login")
            } 
            else if (error.response && error.response.status === 409) {
              setFailModalIsOpen(true)
            } else {
              setOverallFailModalIsOpen(true)
            }
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
      <Header title="Tarif bearbeiten" subtitle="Bearbeite den Tarif mit allen nötigen Daten"/>
      <Formik
        onSubmit={createTarif}
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
                "& > div": {gridColumn: "span 2"} 
              }}
            >
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Tarifname"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.tarifName}
                name="tarifName"
                error={!!touched.tarifName && !!errors.tarifName}
                helperText={touched.tarifName && errors.tarifName}
                InputLabelProps={{
                  style: { color: touched.tarifName && errors.tarifName ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.tarifName && errors.tarifName ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.tarifName && errors.tarifName ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
               <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Preis pro KWh"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.preisKwh}
                name="preisKwh"
                error={!!touched.preisKwh && !!errors.preisKwh}
                helperText={touched.preisKwh && errors.preisKwh}
                InputLabelProps={{
                  style: { color: touched.preisKwh && errors.preisKwh ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.preisKwh && errors.preisKwh ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.preisKwh && errors.preisKwh ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Grundgebühr"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.grundgebuehr}
                name="grundgebuehr"
                error={!!touched.grundgebuehr && !!errors.grundgebuehr}
                helperText={touched.grundgebuehr && errors.grundgebuehr}
                InputLabelProps={{
                  style: { color: touched.grundgebuehr && errors.grundgebuehr ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.grundgebuehr && errors.grundgebuehr ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.grundgebuehr && errors.grundgebuehr ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
               <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Laufzeit"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.laufzeit}
                name="laufzeit"
                error={!!touched.laufzeit && !!errors.laufzeit}
                helperText={touched.laufzeit && errors.laufzeit}
                InputLabelProps={{
                  style: { color: touched.laufzeit && errors.laufzeit ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.laufzeit && errors.laufzeit ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.laufzeit && errors.laufzeit ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Spezielle Konditionen"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.spezielleKonditionen}
                name="spezielleKonditionen"
                error={!!touched.spezielleKonditionen && !!errors.spezielleKonditionen}
                helperText={touched.spezielleKonditionen && errors.spezielleKonditionen}
                InputLabelProps={{
                  style: { color: touched.spezielleKonditionen && errors.spezielleKonditionen ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.spezielleKonditionen && errors.spezielleKonditionen ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.spezielleKonditionen && errors.spezielleKonditionen ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              
            </Box>
            <Box display="flex" justifyContent="space-evenly" mt="20px" gridColumn= "span 8">
            <Button  onClick={() => navigate(-1)} color="neutral" sx={{color: theme.palette.background.default}} variant="contained">
                Abbrechen
              </Button>
              <Button type="submit" sx={{background: colors.color1[400],  color: theme.palette.background.default}} variant="contained">
                Tarif bearbeiten
              </Button>
              <Button onClick={deleteTarif} sx={{background: colors.color5[400],  color: theme.palette.background.default}} variant="contained">
                Tarif löschen
              </Button>
            </Box>
          </form>
        )}
        
      </Formik>

            
    <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Tarif erfolgreich bearbeitet!" navigationGoal="/netzbetreiber/tarifTable"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Tarif konnte nicht geändert werden, da er einem laufenden Vertrag zugewiesen ist"/>
    <SuccessModal open={overallFailModalIsOpen} handleClose={() => setOverallFailModalIsOpen(false)} 
    text="Tarif konnte nicht bearbeitet werden"/>
    <SuccessModal open={deleteModalIsOpen} handleClose={() => setDeleteModalIsOpen(false)}
    text="Tarif erfolgreich gelöscht" navigationGoal="/netzbetreiber/tarifTable"/>
    <SuccessModal open={deleteFailModalisOpen} handleClose={() => setDeleteFailModalisOpen(false)}
    text="Tarif konnte nicht gelöscht werden"/>
    </Box>
  
)}

      

    
const checkoutSchema = yup.object({
  tarifName: yup.string().required("Name ist erforderlich"),
  preisKwh: yup.number().typeError("Kein valider Preis").required("Preis ist erforderlich"),
  grundgebuehr: yup.number().typeError("Kein valider Preis").required("Preis ist erforderlich"),
  laufzeit: yup.number().typeError("Keine valider Laufzeit").required("Laufzeit ist erforderlich"),
  spezielleKonditionen: yup.string(),
});

export default NetzbetreiberTarifEdit;