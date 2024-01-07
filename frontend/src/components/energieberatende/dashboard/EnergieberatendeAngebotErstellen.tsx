import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress } from "@mui/material";
import { NavigateFunction } from "react-router-dom";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import Header from "../../utility/Header";
import { PVAngebotCreate } from "../../../entitities/pv";
import { Orientierung } from "../../../entitities/haushalt";


interface SolarteurePlanErstellenProps {
    angebot: PVAngebotCreate;
    sucessModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    failModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    navigateFN: NavigateFunction
}

const AngebotErstellen = (props: SolarteurePlanErstellenProps) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    const angebotButton = (values: PVAngebotCreate) => {
        const token = localStorage.getItem("accessToken");
        axios.post(addSuffixToBackendURL("solarteure/angebote"), values, {headers: {Authorization: `Bearer ${token}`}})
        .then((response) => {
            props.sucessModalSetter(true);
            props.navigateFN("/solarteure/antragTable");
        })
        .catch((error) => {
            if (error.response.status === 403 || error.response.status === 401) {
                props.navigateFN("/login");
            }
            else {
                props.failModalSetter(true);
            }
            console.log(error);
        })
    }

    const keyMappingAngebot = {
        anlage_id: "Anlage ID",
        modultyp: "Modultyp",
        kapazitaet: "Kapazität",
        installationsflaeche: "Installationsfläche",
        modulanordnung: "Modulanordnung",
        kosten: "Kosten",
    }


    return (
        <>
        <Box mt={5} ml={1} gridColumn={"span 4"}>
   <Header title={"Angebot erstellen"} subtitle="Alle Daten zum Erstellen des Angebots eingeben" variant="h3"/>
    </Box>
   <Box mt={2} ml={1} gridColumn={"span 4"}>
   <Formik
        onSubmit={angebotButton}
        initialValues={props.angebot}
        validationSchema={angebotSchema}
        style={{
          display:"flex",
          flexDirection:"column",
            justifyContent:"center",
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
              gap="10px"
              gridTemplateColumns="repeat(4, minmax(0, 1fr))"
              sx={{
                "& > div": {gridColumn: "span 2"} 
              }}
            >
               {Object.entries(props.angebot).map(([key, value]) => {
                return (
                  <TextField
                    fullWidth
                    variant="outlined"
                    type="text"
                    label={keyMappingAngebot[key]}
                    disabled={key === "anlage_id"}
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
                      '.css-p51h6s-MuiInputBase-input-MuiOutlinedInput-input.Mui-disabled': {
                         "-webkit-text-fill-color": `${colors.color1[500]} !important`,
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
            }}  onClick= {() => props.navigateFN(-1)}>
                Abbrechen
            </Button>
            <Button variant="contained" sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px"
            }}  type="submit">
                Angebot erstellen
            </Button>
            </Box>
            </Box>
          </form>
        )}
        
      </Formik>
      </Box>
        </>
    )

        }


export default AngebotErstellen;

const angebotSchema = yup.object({
    modultyp: yup.string().required("Modultyp ist erforderlich"),
    kapazitaet: yup.number().typeError("Kapazität muss eine Zahl sein").required("Kapazität ist erforderlich"),
    installationsflaeche: yup.number().typeError("Installationsfläche muss eine Zahl sein").required("Installationsfläche ist erforderlich"),
    modulanordnung: yup.string().oneOf(Object.values(Orientierung)).required("Modulanordnung ist erforderlich"),
    kosten: yup.number().typeError("Kosten müssen eine Zahl sein").required("Kosten sind erforderlich"),
})