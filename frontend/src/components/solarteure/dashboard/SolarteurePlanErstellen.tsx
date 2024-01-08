import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress } from "@mui/material";
import { NavigateFunction } from "react-router-dom";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import Header from "../../utility/Header";
import { Orientierung } from "../../../entitities/haushalt";
import { SolarteurResponse, Installationsplan, Schatten, Montagesystem} from "../../../entitities/pv";

interface SolarteurePlanErstellenProps {
    plan: Installationsplan;
    anlageID: number;
    sucessModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    failModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    navigateFN: NavigateFunction
}


const SolarteurePlanErstellen: React.FC<SolarteurePlanErstellenProps> = (props: SolarteurePlanErstellenProps) =>  {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    const keyMapping = {
        "kabelwegfuehrung": "Kabelwegführung",
        "montagesystem": "Montagesystem",
        "schattenanalyse": "Schattenanalyse",
        "wechselrichterposition": "Wechselrichterposition",
        "installationsdatum": "Installationsdatum",
    }

    const planAbschicken = (values: SolarteurePlanErstellenProps) => {
        const token = localStorage.getItem("accessToken");
        console.log(values)
        const url = addSuffixToBackendURL("solarteure/installationsplan/" + props.anlageID);
        const config = {
            headers: {Authorization: `Bearer ${token}`}
        }
        axios.post(url, values, config)
        .then((response) => {
            console.log(response);
            props.sucessModalSetter(true);
        })
        .catch((error) => {
            console.log(error);
            props.failModalSetter(true);
        })    
    }

    return (
        <>
    <Box mt={5} ml={1} gridColumn={"span 4"}>
    <Header title={"Installationsplan erstellen"} subtitle="Alle Daten zum Erstellen des Installationsplan eingeben" variant="h3"/>
    </Box>
    <Box mt={2} ml={1} gridColumn={"span 4"}>
    <Formik
        onSubmit={planAbschicken}
        initialValues={props.plan}
        validationSchema={installationsplanSchema}
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
               {Object.entries({...props.plan, empty:""}).map(([key, value]) => {
                return (
                  <TextField
                    fullWidth
                    variant="outlined"
                    hidden = {key === "empty" ? true : false}
                    type={key === "installationsdatum"? "date" : "text"}
                    label={key === "empty" ? undefined : keyMapping[key]}
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
                Plan abschicken
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


const installationsplanSchema = yup.object({
    kabelwegfuehrung: yup.string().required("Kabelwegführung ist erforderlich"),
    montagesystem: yup.string().oneOf(Object.values(Montagesystem)).required("Montagesystem ist erforderlich"),
    schattenanalyse: yup.string().oneOf(Object.values(Schatten)).required("Schattenanalyse ist erforderlich"),
    wechselrichterposition: yup.string().required("Wechselrichterposition ist erforderlich"),
    installationsdatum: yup.date().required("Installationsdatum ist erforderlich"),
})

export default SolarteurePlanErstellen;