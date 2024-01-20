import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams, useSearchParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import PaymentIcon from '@mui/icons-material/Payment';
import {CircularProgress} from "@mui/material";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import {Rechnung} from "../../../entitities/pv";



const HaushalteRechnungenDetail = ({}) => {

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState<boolean>(false);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState<boolean>(false);
    const [conflictModalIsOpen, setConflictModalIsOpen] = React.useState<boolean>(false);
    const {rechnungID} = useParams();
    const [rechnung, setRechnung] = React.useState<Rechnung>({
        rechnung_id: "",
        empfaenger_id: "",
        steller_id: "",
        rechnungsbetrag: "",
        rechnungsdatum: "",
        faelligkeitsdatum: "",
        rechnungsart: ""
    })

    const keyMapping = {
        rechnung_id: "Rechnungs-ID",
        empfaenger_id: "Empfänger-ID",
        steller_id: "Steller-ID",
        rechnungsbetrag: "Rechnungsbetrag",
        rechnungsdatum: "Rechnungsdatum",
        faelligkeitsdatum: "Fälligkeitsdatum",
        rechnungsart: "Rechnungsart",
        zahlungsstatus: "Zahlungsstatus",
    }



    const navigate = useNavigate();

    useEffect(() => {
            const token = localStorage.getItem("accessToken");
            setStateOtherwiseRedirect(setRechnung, "haushalte/rechnungen/"+rechnungID ,
                navigate,  {Authorization: `Bearer ${token}`}, setIsLoading)
        }, []
    )

    const handleBezahlen = () => {
        const token = localStorage.getItem("accessToken");
        axios.put(addSuffixToBackendURL(`haushalte/rechnungen/${rechnungID}/bezahlen`), {}, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }).then((response) => {
            setSuccessModalIsOpen(true);
        }).catch((error) => {

            if (error.response.status === 412) {
                setConflictModalIsOpen(true);
                return;
            }

            setFailModalIsOpen(true);
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
        <Header title={"Detailübersicht Rechnung "+ rechnungID}
    subtitle="Detaillierte Übersicht über erhaltene Rechnung"/>
    <Box display={"flex"} justifyContent={"space-evenly"}>
    <Button variant="contained" color="primary" onClick={() => {navigate(-1)}}
    sx = {{
        backgroundColor: `${colors.grey[400]} !important`,
            color: theme.palette.background.default
    }}>
    Abbrechen
    </Button>
    <Button variant="contained" color="primary" onClick={handleBezahlen}
    sx = {{
        backgroundColor: `${colors.color1[500]} !important`,
            color: theme.palette.background.default
    }}>
    <PaymentIcon sx={{
        marginRight: "6px",
            marginBottom: "1px"

    }}/>
    Rechnung bezahlen
    </Button>

    </Box>
    <Box gridTemplateColumns={"repeat(4, minmax(0, 1fr))"} display={"grid"}>
        {Object.entries(rechnung).map(([key, value]) => {
                return (
                    <Box gridColumn={(key === "spezielle_konditionen") ? "span 4" : "span 2"} mt={2} ml={1}>
                    <TextField
                        fullWidth
                variant="outlined"
                type="text"
                label={keyMapping[key]}
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
                            background: value === "Gekuendigt_Unbestaetigt" ? colors.color4[400] :
                            value === "Laufend" ? colors.color3[400] :
                                value === "Gekuendigt" ? colors.color5[400] :
                                    undefined
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
        <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)}
    text="Rechnung erfolgreich bezahlt!" navigationGoal="/haushalte/rechnungenOverview"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)}
    text="Rechnung konnte nicht bezahlt werden!"/>
     <SuccessModal open={conflictModalIsOpen} handleClose={() => setConflictModalIsOpen(false)}
    text="Rechnung ist bereits bezahlt!"/>
        </Box>

)
}

export default HaushalteRechnungenDetail;