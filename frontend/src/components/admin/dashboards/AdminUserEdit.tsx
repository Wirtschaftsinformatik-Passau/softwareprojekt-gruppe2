import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import {MenuItem, Select, FormControl, InputLabel, FormHelperText} from "@mui/material";
import { Formik } from "formik";
import * as yup from "yup";
import { tokens } from "../../../utils/theme";
import { useNavigate } from "react-router-dom";
import Header from "../../utility/Header";
import useMediaQuery from "@mui/material/useMediaQuery";
import SuccessModal from "../../utility/SuccessModal";
import {IUser, User, Nutzerrolle, UserDropDownOption} from "../../../entitities/user"
import axios from "axios";
import { Iadresse, Adresse } from "../../../entitities/adress";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";

export class EditableUser{
    public vorname;
    public nachname;
    public telefonnummer;
    public titel;
    public email;
    public rolle;
    public geburtsdatum;
    public passwort;
    public strasse;
    public hausnr;
    public plz;
    public stadt;
    public adresse_id;

    constructor(
        vorname: string,
        nachname: string,
        telefon: string,
        email: string,
        passwort: string,
        rolle:  string,
        geburtsdatum: string,
        strasse: string,
        hausnr: number,
        plz: number,
        stadt: string,
        title: string = "",
        adresse_id: number = 0
    ) {
        this.vorname = vorname;
        this.nachname = nachname
        this.telefonnummer = telefon
        this.email = email
        this.passwort = passwort
        this.rolle = rolle
        this.geburtsdatum = geburtsdatum
        this.adresse_id = adresse_id
        this.titel = title
        this.strasse = strasse
        this.hausnr = hausnr
        this.plz = plz
        this.stadt = stadt  
        this.adresse_id = adresse_id      
    }
}

const extractAdressAndUser = (user: EditableUser) => {
    const adresse: Iadresse = new Adresse(user.strasse, user.hausnr, user.plz, user.stadt, "Deutschland")
    const userToSave: IUser = new User(user.vorname, user.nachname, user.telefonnummer, user.email, 
        user.passwort, user.rolle, user.geburtsdatum, user.adresse_id)
    return {adresse, userToSave}
    
}



const AdminUserEdit: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
  const [userID, setUserID] = React.useState(null)
  const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
  const [isEditing, setIsEditing] = React.useState(false);
  const [editableUser, setEditableUser] = React.useState(null)
  const [initialValues, setInitialValues] = React.useState({vorname: '',
   nachname: '',
   strasse: '',
    hausnr: '',
    plz: '',
    stadt: '',
    geburtstag: '2000-01-01',
    telefon: '',
    nutzerrole: '',
    email: '',
    passwort: '',
    passwortWiederholen: '',
    })

  
    const handleEditButton = () => {
        const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("users/"+userID), {headers: { Authorization: `Bearer ${token}` }})
      .then((response) => {
        if(response.status === 200){
          const user = response.data
          setInitialValues({
            vorname: user.vorname,
            nachname: user.nachname,
            strasse: user.strasse,
            hausnr: user.hausnr,
            plz: user.plz,
            stadt: user.stadt,
            geburtstag: user.geburtsdatum,
            telefon: user.telefonnummer,
            nutzerrole: user.rolle,
            email: user.email,
            passwort: "",
            passwortWiederholen: "",
          })
          setEditableUser(user)
          setIsEditing(true)
        }
      })
      .catch((error) => {
        if (error.response && error.response.status === 401 || error.response.status === 403) {
          navigate("/login")
        }
        else if (error.response && error.response.status === 422) {
          console.log("Server Response on Error 422:", error.response.data);
      }  else if (error.response && error.response.status === 404) {
          setFailModalIsOpen(true)
      }
      else {
          console.log(error);
      }
    }
    )
    }
  
    

 
  const updateUser = (values: any, {setSubmitting}: any) => {
    console.log("hello")
    const { adresse, userToSave: newUser } = extractAdressAndUser(values);
    console.log(adresse);
    console.log(newUser);
    axios.put(addSuffixToBackendURL("users/adresse" + newUser.adresse_id), adresse)
        .then((response) => {
            const adresse_id = response.data.adresse_id
            newUser.adresse_id = adresse_id
            if (response.status === 201) {
                console.log("Adresse erfolgreich gespeichert")
                
                axios.put(addSuffixToBackendURL("users/" + userID), newUser)
                    .then((response) => {
                        if (response.status === 204) {
                            setSuccessModalIsOpen(true)
                            console.log("User erfolgreich gespeichert")
                        }
                    })
                    .catch((error) => {
                        if (error.response && error.response.status === 422) {
                    
                            console.log("Server Response on Error 422:", error.response.data);
                        }else if (error.response && error.response.status === 409) {
                            setFailModalIsOpen(true)
                        }
                              else {
                            console.log(error);
                        }
                    }
                    )
                    .finally(() => {
                        setSubmitting(false);
                    }
                    )
            }
        })
        .catch((error) => {
            if (error.response && error.response.status === 422) {
                console.log("Server Response on Error 422:", error.response.data);
            } else {
                console.log(error);
            }
        })
        .finally(() => {
            setSubmitting(false);
        })


}


  return (
    <>
      <Box m="20px">
        <Header title="Nutzer bearbeiten" subtitle= {isEditing ? "Bearbeite die Daten der Nutzer" : "Wähle die Nutzer ID"} />
      </Box>
      {isEditing ? (
        <Box>
            <Formik
        onSubmit={(updateUser)}
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
                "& > div": { gridColumn: "span 2" },
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
                name="vorname"
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
                name="nachname"
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
                  gridColumn: "span 2",
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
                  gridColumn: "span 2",
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
                  gridColumn: "span 2",
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
                value={values.stadt}
                name="stadt"
                error={!!touched.stadt && !!errors.stadt}
                helperText={touched.stadt && errors.stadt}
                InputLabelProps={{
                  style: { color: touched.stadt && errors.plz ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
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
                  style: { color: touched.geburtstag && errors.geburtstag ? 'red' : `${colors.color1[500]}` ,
                  opacity: values.geburtstag ? 1 : 0}
                  
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
              <TextField
                fullWidth
                variant="outlined"
                type="text"
                label="Telefonnummer"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.telefon}
                name="telefon"
                error={!!touched.telefon && !!errors.telefon}
                helperText={touched.telefon && errors.telefon}
                InputLabelProps={{
                  style: { color: touched.telefon && errors.telefon ? 'red' : `${colors.color1[500]}` }
              }}
              sx={{
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.telefon && errors.telefon ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.telefon && errors.telefon   ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
              <FormControl fullWidth error={!!touched.nutzerrole && !!errors.nutzerrole }
                sx={{
                  gridColumn: "span 2",
                  '& .MuiSvgIcon-root': { 
                      color: touched.nutzerrole && errors.nutzerrole ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiSelect-outlined': { 
                    color: touched.nutzerrole && errors.nutzerrole ? 'red' : `${colors.color1[500]} !important`,
                },
                '& .MuiFormLabel-root': { 
                  color: touched.nutzerrole && errors.nutzerrole ? 'red' : `${colors.color1[500]} !important`,
              },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.nutzerrole && errors.nutzerrole   ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              >
              <InputLabel>Nutzerrolle</InputLabel>
              <Select
                value={values.nutzerrole}
                onChange={handleChange}
                onBlur={handleBlur}
                label="Nutzerrole"
                name="nutzerrole"
              >
                <MenuItem value={Nutzerrolle.Admin}>Admin</MenuItem>
                <MenuItem value={Nutzerrolle.Netzbetreiber}>Netzbetreiber</MenuItem>
                <MenuItem value={Nutzerrolle.Kunde}>Kunde</MenuItem>
                <MenuItem value={Nutzerrolle.Berater}>Berater</MenuItem>
              </Select>
              {touched.nutzerrole && errors.nutzerrole && <FormHelperText>{errors.nutzerrole}</FormHelperText>}
            </FormControl>
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
                  gridColumn: "span 2",
                  '& .MuiInputBase-input': { 
                      color: touched.email && errors.email ? 'red' : `${colors.color1[500]} !important`,
                  },
                  '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: touched.email && errors.email   ? 'red' : `${colors.color1[500]} !important`,
                  },
              }}
              />
            
            </Box>
            <Box display="flex" justifyContent="space-between" mt="20px">
            <Button type="button" sx={{background: theme.palette.neutral.main, color: theme.palette.background.default}} 
            variant="contained"
            onClick={() => setIsEditing(false)}
            >
                Abbrechen
              </Button>
              <Button type="submit" 
              sx={{background: colors.color1[400], color: theme.palette.background.default}} variant="contained">
                Profil bearbeiten
              </Button>
            </Box>
          </form>
        )}
      </Formik>
        </Box>
      ) : (
        <Box component="form"  m="20px" sx={{display: "grid"}}>
            <TextField
            label="Nutzer ID eingeben"
            type="number"
            variant="outlined"
            //@ts-ignore
            onChange={(e) => {
                setUserID(e.target.value)
                console.log(userID)
            }
            }
            InputLabelProps={{
                style: { color: `${colors.color1[500]}` }
            }}
            sx={{
                gridColumn: "span 4",
                '& .MuiInputBase-input': { color: `${colors.color1[500]} !important`,
                },
                '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: `${colors.color1[500]} !important`,
                },
            }}
            />
            <Box sx={{display: "flex", justifyContent: "center", gridColumn: "span 4" , marginTop: "20px"}}>
            <Button variant="contained" sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px",
            }}  onClick={handleEditButton}>
                Auswählen
            </Button>
            </Box>
        </Box>
      )}
      <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Nutzer erfolgreich registriert!" navigationGoal="/admin"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Nutzer ID existiert nicht" />
    </>
  )
      };


      const phoneRegExp = /^\+\d{1,4}\/\d{1,}$/;


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
    

export default AdminUserEdit;