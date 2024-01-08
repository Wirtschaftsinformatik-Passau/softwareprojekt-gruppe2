import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress } from "@mui/material";
import { NavigateFunction } from "react-router-dom";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import Header from "../../utility/Header";
import { EnergieausweisCreate, EnergieeffizienzmassnahmenCreate, MassnahmeTyp } from "../../../entitities/pv";

interface RequestPayloadAuweis {
    energieeffizienzklasse: string;
    gueltigkeit_monate: number | "";
    verbrauchskennwerte: number | "";
}

interface SolarteurePlanErstellenProps {
    ausweis: EnergieausweisCreate;
    massnahmen: EnergieeffizienzmassnahmenCreate;
    sucessModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    energieausweisID: number;
    failModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    navigateFN: NavigateFunction
}

const EnergieberatendeAusweisErstellen = (props: SolarteurePlanErstellenProps) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    const ausweisErstellen = (values: EnergieausweisCreate) => {
        const token = localStorage.getItem("accessToken");
        const payload: RequestPayloadAuweis = {
          energieeffizienzklasse: values.energieeffizienzklasse,
          gueltigkeit_monate: Number(values.gueltigkeit),
          verbrauchskennwerte: Number(values.verbrauchskennwerte),
        }
        axios.post(addSuffixToBackendURL("energieberatende/energieausweis-erstellen/" + props.energieausweisID),
         payload, {headers: {Authorization: `Bearer ${token}`}})
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

    const keyMappingAusweis = {
      energieeffizienzklasse: "Energieeffizienzklasse",
      gueltigkeit: "Gültigkeit in Monaten",
      verbrauchskennwerte: "Verbrauchskennwerte",
    }

    const keyMappingMassnahmen = {
      massnahmetyp: "Energieeffizienzmaßnahme",
      kosten: "Kosten",
      einsparpotential: "Einsparpotenzial",
    }


    return (
        <>
        <Box mt={5} ml={1} gridColumn={"span 4"}>
   <Header title={"Energieausweis erstellen"} subtitle="Alle Daten zum Erstellen des Energiesausweises eingeben" variant="h3"/>
    </Box>
   <Box mt={2} ml={1} gridColumn={"span 4"}>
   <Formik
        onSubmit={ausweisErstellen}
        initialValues={props.ausweis}
        validationSchema={ausweisSchema}
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
               {Object.entries({...props.ausweis, empty:""}).map(([key, value]) => {
                return (
                  <TextField
                    fullWidth
                    
                    variant="outlined"
                    type="text"
                    label={key === "empty" ? undefined : keyMappingAusweis[key]}
                    disabled={key === "empty"}
                    onBlur={handleBlur}
                    onChange={handleChange}
                    value={key === "empty" ? undefined : values[key]}
                    name={key === "empty" ? undefined : key}
                    error={!!touched[key] && !!errors[key]}
                    helperText={touched[key] && errors[key]}
                    InputLabelProps={{
                      style: { color: touched[key] && errors[key] ? 'red' : `${colors.color1[500]}` }
                  }}
                  sx={{
                      gridColumn: "span 2",
                      '& .MuiInputBase-input': { 
                          color: key === "empty" ? theme.palette.background.default : touched[key] && errors[key] ? 'red' : `${colors.color1[500]} !important`,
                      },
                      '.css-p51h6s-MuiInputBase-input-MuiOutlinedInput-input.Mui-disabled': {
                         "-webkit-text-fill-color": `${colors.color1[500]} !important`,
                      },
                      '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: key === "empty" ? theme.palette.background.default : touched[key] && errors[key] ? 'red' : `${colors.color1[500]} !important`,
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
                Ausweis erstellen
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


export default EnergieberatendeAusweisErstellen;

const ausweisSchema = yup.object({
    energieeffizienzklasse: yup.string().required("Energieeffizienzklasse ist erforderlich"),
    gueltigkeit: yup.number().typeError("Monate als Zahl eingeben").required("Gültigkeit ist erforderlich"),
    verbrauchskennwerte: yup.number().typeError("Nur Dezimalzahlen erlaubt").required("Verbraucherkennwerte sind erforderlich"),
  });

  const massnahmenSchema = yup.object({
    massnahmetyp: yup.string().oneOf(Object.values(MassnahmeTyp)).required("Maßnahmentyp ist erforderlich"),
    kosten: yup.number().required("Kosten sind erforderlich"),
    einsparpotenzial: yup.number().required("Einsparpotenzial ist erforderlich"),
  });