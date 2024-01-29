import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress } from "@mui/material";
import { NavigateFunction } from "react-router-dom";
import CircularProgress from '@mui/material/CircularProgress';
import { tokens } from "../../../utils/theme";
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import Header from "../../utility/Header";
import {EnergieberaterResponseFinal} from "../../../entitities/pv";
import {setStateOtherwiseRedirect} from "../../../utils/stateUtils";

interface EnergieberaterAbnahmeProps {
    anlageID: number;
    sucessModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
    navigateFN: NavigateFunction
    failModalSetter: React.Dispatch<React.SetStateAction<boolean>>;
}

const EnergieberaterAbnahme = (props: EnergieberaterAbnahmeProps) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [anlage, setAnlage] = React.useState<EnergieberaterResponseFinal | null>(null);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);

    const keyMappingAnlage = {
        anlage_id: "Anlage ID",
        haushalt_id: "Haushalt ID",
        solarteur_id: "Solarteur ID",
        modultyp: "Modultyp",
        kapazitaet: "Kapazität",
        installationsflaeche: "Installationsfläche",
        installationsdatum: "Installationsdatum",
        installationsstatus: "Installationsstatus",
        modulanordnung: "Modulanordnung",
        kabelwegfuehrung: "Kabelwegführung",
        montagesystem: "Montagesystem",
        schattenanalyse: "Schattenanalyse",
        wechselrichterposition: "Wechselrichterposition",
        installationsplan: "Installationsplan",
        prozess_status: "Prozess Status",
        nvpruefung_status: "NVP Status",
        vorname: "Vorname",
        nachname: "Nachname",
        email: "Email",
        strasse: "Straße",
        hausnummer: "Hausnummer",
        plz: "PLZ",
        stadt: "Stadt",
}

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setAnlage, "energieberatende/anfragen/" + props.anlageID,
            props.navigateFN, {Authorization: `Bearer ${token}`}, setIsLoading)
    }, []);

    //TODO: 412 kommt --> handlen
    const abnahmeBestaetigen = () => {
        const token = localStorage.getItem("accessToken");
        axios.put(addSuffixToBackendURL("energieberatende/abnahme-pvanlage/" + props.anlageID),
            {}, {headers: {Authorization: `Bearer ${token}`}})
            .then((response) => {
                props.sucessModalSetter(true);
            })
            .catch((error) => {
                if (error.response.status === 403 || error.response.status === 401) {
                    props.navigateFN("/login");
                } else {
                    props.failModalSetter(true);
                }
                console.log(error);
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
        <>
            <Box display={"flex"} justifyContent={"space-evenly"} gridColumn={"span 4"}>
                <Button variant="contained" color="primary" onClick={() => {props.navigateFN(-1)}}
                        sx = {{
                            backgroundColor: `${colors.grey[400]} !important`,
                            color: theme.palette.background.default
                        }}>
                    Abbrechen
                </Button>
                <Button variant="contained" color="primary" onClick={abnahmeBestaetigen}
                        sx = {{
                            backgroundColor: `${colors.color1[400]} !important`,
                            color: theme.palette.background.default
                        }}>
                    Anlage abnehmen
                </Button>
                </Box>
            <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"} gridColumn={"span 4"}>
                {Object.entries(anlage).map(([key, value], index) => {
                    return (
                        key == "haushalt_id" || key == "anlage_id" || key == "energieausweis_id" ? undefined :
                            <Box key={index} gridColumn={(key === "stadt") ? "span 4" : "span 2"} mt={2} ml={1}>
                                <TextField
                                    fullWidth
                                    variant="outlined"
                                    type="text"
                                    label={keyMappingAnlage[key]}
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
            </>
    )}


export default EnergieberaterAbnahme;

