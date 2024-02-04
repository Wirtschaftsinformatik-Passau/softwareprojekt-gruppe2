import { Box, Button, TextField } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import React from "react";
import { useNavigate } from "react-router-dom";
import { CssBaseline } from "@material-ui/core";
import useMediaQuery from "@mui/material/useMediaQuery";
import Header from "../../utility/Header";
import { useTheme } from "@mui/material/styles";
import { tokens } from "../../../utils/theme";
import SuccessModal from "../../utility/SuccessModal";
import {IUser, User, Nutzerrolle, UserDropDownOption} from "../../../entitities/user"
import {MenuItem, Select, FormControl, InputLabel, FormHelperText} from "@mui/material";
import axios from "axios";
import { ITarif, Tarif } from "../../../entitities/tarif";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";


const NetzbetreiberTarifCreate = () => {
  const navigate = useNavigate();
  const isNonMobile = useMediaQuery("(min-width:600px)");
  const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
  const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);



  const createTarif = (values: any, {setSubmitting}: any) => {

    const token = localStorage.getItem("accessToken");
    const tarif: ITarif = new Tarif(values.tarifName, Number(values.preisKwh), Number(values.grundgebuehr), Number(values.laufzeit), 
    values.spezielleKonditionen)
    axios.post(addSuffixToBackendURL("netzbetreiber/tarife"), tarif, {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
          if (response.status === 201) {
            setSuccessModalIsOpen(true)
            console.log("User erfolgreich gespeichert")
          } else {
            setFailModalIsOpen(true)
            console.log("User konnte nicht gespeichert werden")
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
              console.log("Tarif konnte nicht gespeichert werden")
            } else {
              console.log("Server Error:", error.message);
            }
        })
        .finally(() => {
            setSubmitting(false);
        })


}

  return (
    <Box m="20px">
      <Header title="Tarif erstellen" subtitle="Erstelle einen neuen Tarif mit allen nötigen Daten"/>
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
                "& > div": { gridColumn: isNonMobile ? undefined : "span 4" },
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
                  gridColumn: "span 4",
                  '& .MuiInputBase-input': { 
                      color: touched.spezielleKonditionen && errors.spezielleKonditionen ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.spezielleKonditionen && errors.spezielleKonditionen ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              
            <Box display="flex" justifyContent="end" mt="20px" gridColumn= "span 4">
              <Button type="submit" sx={{background: colors.color1[400],  color: theme.palette.background.default}} variant="contained">
                Tarif erstellen
              </Button>
            </Box>
            </Box>
          </form>
        )}
        
      </Formik>
            
    <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Tarif erfolgreich erstellt!" navigationGoal="/netzbetreiber"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Tarifname bereits vergeben"/>
    </Box>
  
  );
};



  const checkoutSchema = yup.object({
    tarifName: yup.string().required("Name ist erforderlich"),
    preisKwh: yup.number().typeError("Kein valider Preis").required("Preis ist erforderlich"),
    grundgebuehr: yup.number().typeError("Kein valider Preis").required("Preis ist erforderlich"),
    laufzeit: yup.number().typeError("Keine valider Laufzeit").required("Laufzeit ist erforderlich"),
    spezielleKonditionen: yup.string(),
});

  const initialValues = {
    tarifName: "",
    preisKwh: "",
    grundgebuehr: "",
    laufzeit: "",
    spezielleKonditionen: "",
};

export default NetzbetreiberTarifCreate;