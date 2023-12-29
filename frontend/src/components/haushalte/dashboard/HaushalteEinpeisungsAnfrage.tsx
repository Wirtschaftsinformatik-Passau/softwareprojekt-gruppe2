import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";





const Anfrage = () => {
  const navigate = useNavigate();
  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
  const [tarifId, setTarifId] = React.useState(0)


  
    const handleEditButton = () => {
        const token = localStorage.getItem("accessToken");
        axios.get(addSuffixToBackendURL("netzbetreiber/tarife/"+tarifId), {headers: { Authorization: `Bearer ${token}` }})
      .then((response) => {
        if(response.status === 200){
          console.log(tarifId)
          navigate("/netzbetreiber/tarifEdit/"+Number(tarifId))
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
  
  return (
    <>
      <Box m="20px">
        <Header title="PV Anlage anfragen" subtitle= {"PV Anlage für aktuellen Haushalt beantragen"} />
      </Box>
        <Box component="form"  m="20px" sx={{display: "grid"}}>
            
            <Box sx={{display: "flex", justifyContent: "center", gridColumn: "span 8" , marginTop: "20px"}}>
            <Button variant="contained" sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px",
                width: "100%",
            }}  onClick={handleEditButton}>
                Anfrage abschicken
            </Button>
            </Box>
        </Box>
      
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Tarif ID existiert nicht" />
    </>
  )
      };


      



    

export default Anfrage;