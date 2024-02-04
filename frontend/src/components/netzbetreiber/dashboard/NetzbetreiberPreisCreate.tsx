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
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import {IPreis, Preis} from "./NetzbetreibePreisEditCustom"


const NetzbetreiberPreisCreation = () => {
  const navigate = useNavigate();
  const isNonMobile = useMediaQuery("(min-width:600px)");
  const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
  const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);



  const createPreis = (values: any, {setSubmitting}: any) => {

    const token = localStorage.getItem("accessToken");
    const preis = new Preis(Number(values.bezugspreis), Number(values.einspeisepreis))
    axios.post(addSuffixToBackendURL("netzbetreiber/preisstrukturen"), preis, {headers: {Authorization: `Bearer ${token}`}})
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
      <Header title="Preis erstellen" subtitle="Erstelle eine neue Preisstruktur"/>
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
                "& > div": { gridColumn: isNonMobile ? undefined : "span 4" },
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
              
            <Box display="flex" justifyContent="end" mt="20px" gridColumn= "span 4">
              <Button type="submit" sx={{background: colors.color1[400],  color: theme.palette.background.default}} variant="contained">
                Preisstruktur erstellen
              </Button>
            </Box>
            </Box>
          </form>
        )}
        
      </Formik>
            
    <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Preisstruktur erfolgreich erstellt!" navigationGoal="/netzbetreiber"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Preiserstellung nicht möglich"/>
    </Box>
  
  );
};



const checkoutSchema = yup.object({
    bezugspreis: yup.number().typeError("Muss eine Zahl sein").test('input1-or-input2', 'Bitte Bezugspreis oder Einspeisepreis oder beide angeben', function(value) {
        const { einspeisepreis } = this.parent;
        return value || einspeisepreis}),
    einspeisepreis: yup.number().typeError("Muss eine Zahl sein").test('input1-or-input2', 'Bitte Bezugspreis oder Einspeisepreis oder beide angeben', function(value) {
        const { bezugspreis } = this.parent;
        return value || bezugspreis})})

const initialValues = {
    bezugspreis: "",
    einspeisepreis: "",
}

    

export default NetzbetreiberPreisCreation;