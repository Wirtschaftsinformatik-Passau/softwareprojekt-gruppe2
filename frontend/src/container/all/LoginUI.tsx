import { Box, Button, TextField , useTheme} from "@mui/material";
import React  from "react";
import { useNavigate } from "react-router-dom";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../utils/theme";
import { inputLabelClasses } from "@mui/material/InputLabel";
import { alpha } from "@material-ui/core/styles";
import {makeStyles} from "@material-ui/core/styles";
import axios from "axios";
import Header from "../../components/utility/Header";
import Topbar from "../../components/admin/dashboards/Topbar";
import useMediaQuery from "@mui/material/useMediaQuery";
import { Paper } from '@mui/material';
import panelImg from "../../assets/solar_login2.jpg";

import {ILoginUser, LoginUser } from '../../entitities/user';
import { addSuffixToBackendURL } from '../../utils/networking_utils';
import LoginDialog from "../../components/all/login/LoginDialog";
import WrongPasswordModal from "../../components/all/login/WrongPasswordModal";
import SuccessModal from "../../components/utility/SuccessModal";

const LoginSchema = yup.object().shape({
    email: yup.string().email("Invalid email").required("Required"),
    password: yup.string().min(3, "Password must be at least 4 characters long").required("Required"),
})

const LoginUI = () => {
    const isNonMobile = useMediaQuery("(min-width: 768px)");
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [vergessenOpen, setVergessenOpen] = React.useState(false);
    const [email, setEmail] = React.useState("")    
    const [password, setPassword] = React.useState("")
    const [modalisOpen, setModalIsOpen] = React.useState(false);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
    const navigate = useNavigate();

    const handleVergessenOpen = () => {
        setVergessenOpen(true);
    }

    const handleVergessenClose = () => {
        setVergessenOpen(false);
    }


    const checkLogin = (values: any, {setSubmitting}: any) => {
        const user = new LoginUser(values.email, values.password);
        console.log(user)
        axios.post(addSuffixToBackendURL("auth/login"), user)
        .then((response) => {
            console.log(response)
            if(response.status === 202){
                const accessToken = response.data.access_token
                localStorage.setItem("accessToken", accessToken)
                console.log("accessToken: ", accessToken)   
                navigate("/admin")
            }
            else{
                setModalIsOpen(true)
            }
        
        })
        .catch((error) => {
            if ((error.response && error.response.status === 404) || (error.response && error.response.status === 401)){
                setModalIsOpen(true)
            }
            else {
                console.log(error.response.data);
            }
        }
        )
        .finally(() => {
            setSubmitting(false); // Set Formik submitting state to false
        });
        
    }


    return (
        <div>
        <Topbar fixed={true}/>
        <div className="flex justify-start items-center flex-col h-screen" >
        <div className=" relative w-full h-full bg-white">
        <img src={panelImg} alt="solar panel"
                    className="w-full h-full object-cover"/>
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
        <Header title="GreenEcoHub" subtitle="Bitte Zugangsdaten eingeben" />
        <Formik
    onSubmit={checkLogin}
    initialValues={{
        email: "",
        password: "",
    }}
    validationSchema={LoginSchema}
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
                "& > div": { gridColumn: isNonMobile ? undefined : "span 4" }
            }}>
                <TextField
        fullWidth
        variant="outlined"
        type="text"
        label="E-Mail"
        onBlur={handleBlur}
        onChange={handleChange}
        value={values.email}
        name="email"
        error={!!touched.email && !!errors.email}
        helperText={touched.email && errors.email}
        InputLabelProps={{
            style: { color: touched.email && errors.email ? 'red' : `${colors.color1[500]}` }
        }}
        sx={{
            gridColumn: isNonMobile ? "2 / span 2" : "span 4",
            '& .MuiInputBase-input': { 
                color: touched.email && errors.email ? 'red' : `${colors.color1[500]} !important`,
            },
            '& .MuiOutlinedInput-notchedOutline': {
                borderColor: touched.email && errors.email ? 'red' : `${colors.color1[500]} !important`,
            },
        }}
    />
                <TextField
                    fullWidth
                    variant="outlined"
                    type="password"
                    label="Passwort"
                    onBlur={handleBlur}
                    onChange={handleChange}
                    value={values.password}
                    name="password"
                    error={!!touched.password && !!errors.password}
                    helperText={touched.password && errors.password}
                    InputLabelProps={{
                        style: { color: touched.password && errors.password ? 'red' : `${colors.color1[500]}` }
                    }}
                    sx={{
                        gridColumn: isNonMobile ? "2 / span 2" : "span 4",
                        '& .MuiInputBase-input': { 
                            color: touched.password && errors.password ? 'red' : `${colors.color1[500]} !important`,
                        },
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: touched.password && errors.password ? 'red' : `${colors.color1[500]} !important`,
                        },
                    }}
                />
                </Box>
                <div className="grid grid-cols-3 gap-4">
                <Box display={"flex"} justifyContent={"center"} mt="20px" >
                    <Button type="button" variant="contained" color="neutral" sx={{
                        borderRadius: "10px",
                    }} onClick={() => navigate("/registration")}>
                        Registrieren
                    </Button>
                </Box>
                <Box display={"flex"} justifyContent={"center"} mt="20px" >
                    <Button type="button" variant="contained" color="neutral" sx={{
                        borderRadius: "10px",
                    }} onClick={(handleVergessenOpen)}>
                        Passwort Vergessen
                    </Button>
                </Box>
                <Box display={"flex"} justifyContent={"center"} mt="20px" >
                    <Button type="submit" variant="contained" color="secondary" sx={{
                        borderRadius: "10px",
                    }} onClick={() => setSuccessModalIsOpen(true)}>
                        Einloggen
                    </Button>
                </Box>
                </div>
        </form>
    )}
</Formik>
<LoginDialog open={vergessenOpen} handleClose={handleVergessenClose}/>
<WrongPasswordModal open={modalisOpen} handleClose={() => setModalIsOpen(false)}/>
<SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} text="Password falsch!" navigationGoal="/registration"/>
        </Paper>
        </div>
        </div>
        </div>
        </div>
    )
}

export default LoginUI;

