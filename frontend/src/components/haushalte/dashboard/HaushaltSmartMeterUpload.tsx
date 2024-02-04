import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress} from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useNavigate , useParams} from "react-router-dom";
import Header from "../../utility/Header";
import SuccessModal from "../../utility/SuccessModal";
import axios from "axios";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { IUser } from "../../../entitities/user";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";


export interface IUserFull extends IUser {
    user_id: number
}

const HaushalteSmartMeterUpload = () => {
  const navigate = useNavigate();  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [isUploading, setIsUploading] = React.useState(false)
  const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
  const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [currentUser, setCurrentUser] = React.useState<IUserFull | null>(null)


  const uploadFile = (event : React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
        const file = event.target.files[0];
        if (file.type !== "text/csv") {
           setFailModalIsOpen(true);
           return
        }
      setSelectedFile(file);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setCurrentUser, "users/current/single", navigate, {Authorization: `Bearer ${token}`})
  }, [])

  

  const sendFile = () => {
    setIsUploading(true);
    const token = localStorage.getItem("accessToken");
    const formData = new FormData();
    if (selectedFile) {
      formData.append("file", selectedFile);
    }
    const userID = currentUser?.user_id
    axios.post(addSuffixToBackendURL("netzbetreiber/dashboard/" + userID), formData, {headers: { Authorization: `Bearer ${token}` }})
    .then((res) => {
      console.log(res.data)
      setSuccessModalIsOpen(true)
    })
    .catch((err) => {
      console.log(err.response.data)
    })
    .finally(() => {
        setIsUploading(false)
    })
  }

  
    
  
  return (
    <>
      <Box m="20px">
        <Header title="Smart Meter Daten" subtitle= {"Upload der Smart Meter Daten"} />
      </Box>
        <Box component="form"  m="20px" sx={{display: "grid"}}>
            
            <Box sx={{display: "flex", justifyContent: "center", gridColumn: "span 8" , marginTop: "20px"}}>
            <Button variant="contained"
            component="label"
            sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px",
                width: "100%",
            }}  onClick={uploadFile}>
                Upload
            <input
                type="file"
                hidden
                onChange={uploadFile}
            />
            </Button>
            </Box>
            </Box>
            {selectedFile && 
            <Box gridTemplateColumns={"repeat(8, minmax(0, 1fr))"} display={"grid"} width={"100%"}>
            <Box
            sx={{justifyContent: "center", gridColumn: "span 4" , marginTop: "0px" }}>
                <Box>
            <Typography sx={{display: "grid", justifyContent: "center", gridColumn: "span 4" , marginTop: "0px", color:"blue", padding: "10px 20px", borderRadius:"5px"
            }} border={`1px solid ${colors.color1[400]}`}> 
            <a href={URL.createObjectURL(selectedFile)} target="_blank" rel="noopener noreferrer">
            {selectedFile.name}
            </a>
            </Typography>
            </Box>
            </Box>
            <Box sx={{justifyContent:"center",  gridColumn: "span 4"}}>
            <Button variant="contained"
            component="label"
            sx= {{
                backgroundColor: `${colors.color1[400]} !important`,
                color: theme.palette.background.default,
                padding: "10px 20px",
                width: "100%",
            }}  onClick={sendFile}>
                Abschicken
            </Button>
            </Box>
            </Box>
}
{isUploading && 
    <>
    <Box marginTop="10px">
    <LinearProgress sx={{ bgcolor: colors.color1[400] }}/>
    </Box>
    </>}
        <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
        text="Bitte nur CSV Dateien hochladen!" />
        <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
        text="Daten erfolgreich abgeschickt!" navigationGoal="/haushalte/"/>
    </>
  )
      };


      



    

export default HaushalteSmartMeterUpload;