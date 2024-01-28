import { Box, Button, TextField , useTheme} from "@mui/material";
import React, { useEffect }  from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../utils/theme";
import { alpha } from "@material-ui/core/styles";
import axios from "axios";
import Header from "../../components/utility/Header";
import Topbar from "../../components/all/Topbar"
import { Paper } from '@mui/material';
import { addSuffixToBackendURL, setStateofResponse } from '../../utils/networking_utils';
import SuccessModal from "../../components/utility/SuccessModal";
import { er } from "@fullcalendar/core/internal-common";

interface PasswordForgotParams {
    passwort: string;
    passwortWiederholen: string;
}

const PasswordReset = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const [successModalText, setSuccessModalText] = React.useState("Passwort erfolgreich geändert.")
    const navigate = useNavigate();
    const {token} = useParams()
    
    const resetPassword = (values: PasswordForgotParams) => {
        const accessToken = localStorage.getItem("accessToken")
        axios.post(addSuffixToBackendURL("users/reset-passwort/" + token), {
            neu_passwort: values.passwort
        }, {headers: {Authorization: `Bearer ${accessToken}`}}).then((response) => {
            setSuccessModalIsOpen(true)
        })
        .catch((error) => {
            switch (error.response.status) {
                case 403:
                    setSuccessModalText("Dein Link ist abgelaufen. Bitte fordere einen neuen Link an.")
                    break;
                case 404:
                    setSuccessModalText("Dein Link ist ungültig. Bitte fordere einen neuen Link an.")
                    break;
                default:
                    setSuccessModalText("Es ist ein Fehler aufgetreten. Bitte versuche es später erneut.")
                    break;
            }
            setSuccessModalIsOpen(true)
        })
    }

    return (
        <div>
        <Topbar fixed={true} search={false} nutzerrolle={null}/>
        <div className="flex justify-start items-center flex-col h-screen" >
        <div className=" relative w-full h-full bg-white">
        <div className="absolute flex flex-col justify-center items-center top-0 left-0 right-0 bottom-0">
        
        <Paper elevation={6} 
                            sx={{ 
                                maxWidth: '500px',
                                width: '100%',
                                margin: 'none', 
                                padding: '4rem', 
                                background: alpha('#f5f7fa', 0.8), 
                                borderRadius: '15px', 
                            }}>
        <Header title="GreenEcoHub" subtitle="Bitte neues Passwort eingeben" />
        <Formik
    onSubmit={resetPassword}
    initialValues={{
        passwort: "",
        passwortWiederholen: "",
    }}
    validationSchema={PasswordForgotSchema}
>
    {({
        values, 
        errors,
        touched,
        handleBlur,
        handleChange,
        handleSubmit
    }) => (
        <form onSubmit={handleSubmit}>
            <Box display={"grid"} gridTemplateColumns={"repeat(4, 1fr)"} gap="2rem" sx={{
                "& > div": "span 4"
            }}>
                <TextField
        fullWidth
        variant="outlined"
        type="password"
        label="Passwort"
        onBlur={handleBlur}
        onChange={handleChange}
        value={values.passwort}
        name="passwort"
        error={!!touched.passwort && !!errors.passwort}
        helperText={touched.passwort && errors.passwort}
        InputLabelProps={{
            style: { color: touched.passwort && errors.passwort ? 'red' : `${colors.color1[500]}` }
        }}
        sx={{
            gridColumn: "span 4",
            '& .MuiInputBase-input': { 
                color: touched.passwort && errors.passwort ? 'red' : `${colors.color1[500]} !important`,
            },
            '& .MuiOutlinedInput-notchedOutline': {
                borderColor: touched.passwort && errors.passwort ? 'red' : `${colors.color1[500]} !important`,
            },
        }}
    />
                <TextField
                    fullWidth
                    variant="outlined"
                    type="password"
                    label="Passwort wiederholen"
                    onBlur={handleBlur}
                    onChange={handleChange}
                    value={values.passwortWiederholen}
                    name="passwortWiederholen"
                    error={!!touched.passwortWiederholen && !!errors.passwortWiederholen}
                    helperText={touched.passwortWiederholen && errors.passwortWiederholen}
                    InputLabelProps={{
                        style: { color: touched.passwortWiederholen && errors.passwortWiederholen ? 'red' : `${colors.color1[500]}` }
                    }}
                    sx={{
                        gridColumn: "span 4",
                        '& .MuiInputBase-input': { 
                            color: touched.passwortWiederholen && errors.passwortWiederholen ? 'red' : `${colors.color1[500]} !important`,
                        },
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: touched.passwortWiederholen && errors.passwortWiederholen ? 'red' : `${colors.color1[500]} !important`,
                        },
                    }}
                />
                </Box>
                <Box display={"flex"} justifyContent={"space-between"} mt="20px" >
                 <Button onClick={() => navigate("/login")} variant="contained" color="neutral" sx={{
                        borderRadius: "10px",
                    }}>
                        Zurück
                    </Button>
                    <Button type="submit" variant="contained" color="secondary" sx={{
                        borderRadius: "10px",
                    }}>
                        Bestätigen
                    </Button>
                </Box>
                
        </form>
    )}
</Formik>
<SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} text={successModalText}/>
</Paper>
        </div>
        </div>
        </div>
        </div>
)}

export default PasswordReset;


const PasswordForgotSchema = yup.object().shape({
 passwort: yup.string().min(3, 'Das Passwort muss mindestens 3 Zeichen lang sein').required('Passwort ist erforderlich'),
 passwortWiederholen: yup.string().oneOf([yup.ref('passwort'), null], 'Passwörter müssen übereinstimmen').required('Passwortbestätigung ist erforderlich'),

});
                    