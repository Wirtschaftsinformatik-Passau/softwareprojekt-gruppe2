import { Box, Button, TextField } from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { CssBaseline } from "@material-ui/core";
import useMediaQuery from "@mui/material/useMediaQuery";
import Header from "../../components/utility/Header";
import Topbar from "../../components/all/dashboards/Topbar";
import { useTheme } from "@mui/material/styles";
import { tokens } from "../../utils/theme";
import solarImg from "../../assets/solar_high.jpg"
import {IUser, User, Nutzerrolle, UserDropDownOption} from "../../entitities/user"
import { Iadresse, Adresse } from "../../entitities/adress";
import { addSuffixToBackendURL } from "../../utils/networking_utils";

const Form = () => {
  const isNonMobile = useMediaQuery("(min-width:600px)");
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const handleFormSubmit = (values: any) => {
    console.log(values);
  };

  return (
    <div>
    <Topbar fixed={true}/>
    <div className="flex justify-start items-center flex-col h-screen" style={{marginTop: "70px"}}>
    <div className={`w-full h-full ${theme.palette.mode == "dark" ? "bg-gray-100" : "bg-gray-600"} flex flex-row`}>
       
    <Box
          sx={{
            width: '50%',
            marginRight: "10px",
            padding: "20px",
          }}
        >
      <Header title="Registrieren" subtitle="Erstelle ein neues Nutzerprofil"/>
      <Formik
        onSubmit={handleFormSubmit}
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
                label="Vorname"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.vorname}
                name="firstName"
                error={!!touched.vorname && !!errors.vorname}
                helperText={touched.vorname && errors.vorname}
                InputLabelProps={{
                  style: { color: touched.vorname && errors.vorname ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.vorname && errors.vorname ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.vorname && errors.vorname ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
               <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Nachname"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.nachname}
                name="firstName"
                error={!!touched.nachname && !!errors.nachname}
                helperText={touched.nachname && errors.nachname}
                InputLabelProps={{
                  style: { color: touched.nachname && errors.nachname ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.nachname && errors.nachname ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.nachname && errors.nachname ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Straße"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.strasse}
                name="strasse"
                error={!!touched.strasse && !!errors.strasse}
                helperText={touched.strasse && errors.strasse}
                InputLabelProps={{
                  style: { color: touched.strasse && errors.strasse ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 1",
                  '& .MuiInputBase-input': { 
                      color: touched.strasse && errors.strasse ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.strasse && errors.strasse ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
               <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Hausnr."
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.hausnr}
                name="hausnr"
                error={!!touched.hausnr && !!errors.hausnr}
                helperText={touched.hausnr && errors.hausnr}
                InputLabelProps={{
                  style: { color: touched.hausnr && errors.hausnr ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 1",
                  '& .MuiInputBase-input': { 
                      color: touched.hausnr && errors.hausnr ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.hausnr && errors.hausnr ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Postleitzahl"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.plz}
                name="plz"
                error={!!touched.plz && !!errors.plz}
                helperText={touched.plz && errors.plz}
                InputLabelProps={{
                  style: { color: touched.plz && errors.plz ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 1",
                  '& .MuiInputBase-input': { 
                      color: touched.plz && errors.plz ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.plz && errors.plz ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Stadt"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.plz}
                name="stadt"
                error={!!touched.stadt && !!errors.stadt}
                helperText={touched.stadt && errors.stadt}
                InputLabelProps={{
                  style: { color: touched.stadt && errors.plz ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 1",
                  '& .MuiInputBase-input': { 
                      color: touched.stadt && errors.stadt ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.stadt && errors.stadt ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
            <TextField
                fullWidth
                variant="outlined"
                type="date"
                label="Geburtstag"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.geburtstag}
                name="geburtstag"
                error={!!touched.geburtstag && !!errors.geburtstag}
                helperText={touched.geburtstag && errors.geburtstag}
                InputLabelProps={{
                  style: { color: touched.geburtstag && errors.geburtstag ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.geburtstag && errors.geburtstag ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.geburtstag && errors.geburtstag   ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
            </Box>
            <Box display="flex" justifyContent="end" mt="20px">
              <Button type="submit" color="secondary" variant="contained">
                Profil erstellen
              </Button>
            </Box>
          </form>
        )}
      </Formik>
      </Box>
      <Box
          sx={{
            width: '50%',
            backgroundColor: "blue"
          }}
        >
          <img src={solarImg} style={{width: "100%", height: "100%"}}/>
        </Box>
     
    </div>
    </div>
    </div>
  
  );
};

const phoneRegExp =
  /^((\+[1-9]{1,4}[ -]?)|(\([0-9]{2,3}\)[ -]?)|([0-9]{2,4})[ -]?)*?[0-9]{3,4}[ -]?[0-9]{3,4}$/;

  const checkoutSchema = yup.object({
    vorname: yup.string().required('Vorname ist erforderlich'),
    nachname: yup.string().required('Nachname ist erforderlich'),
    strasse: yup.string().required('Straße ist erforderlich'),
    hausnr: yup.number().typeError("Keine valide Hausnummer").required('Hausnummer ist erforderlich'),
    plz: yup.string().matches(/^\d{5}$/, 'PLZ muss 5 Ziffern lang sein').required('PLZ ist erforderlich'),
    stadt: yup.string().required('Stadt ist erforderlich'),
    geburtstag: yup.date().typeError("Kein valides Datum").required('Geburtstag ist erforderlich'),
    telefon: yup.string().matches(phoneRegExp, 'Telefonnummer ist nicht gültig').required('Telefonnummer ist erforderlich'),
    nutzerrole: yup.string().oneOf([Nutzerrolle.Admin, Nutzerrolle.Berater, Nutzerrolle.Kunde, Nutzerrolle.Netzbetreiber], 'Ungültige Nutzerrolle').required('Nutzerrolle ist erforderlich'),
    email: yup.string().email('E-Mail ist ungültig').required('E-Mail ist erforderlich'),
    passwort: yup.string().min(8, 'Das Passwort muss mindestens 8 Zeichen lang sein').required('Passwort ist erforderlich'),
    passwortWiederholen: yup.string().oneOf([yup.ref('passwort'), null], 'Passwörter müssen übereinstimmen').required('Passwortbestätigung ist erforderlich'),
  });

  const initialValues = {
    vorname: '',
    nachname: '',
    strasse: '',
    hausnr: '',
    plz: '',
    stadt: '',
    geburtstag: '',
    telefon: '',
    nutzerrole: '',
    email: '',
    passwort: '',
    passwortWiederholen: '',
  };

export default Form;