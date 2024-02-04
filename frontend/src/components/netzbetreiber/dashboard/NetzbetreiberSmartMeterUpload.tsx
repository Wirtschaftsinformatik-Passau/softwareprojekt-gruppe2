import React, { useEffect } from "react";
import { Box, Button, TextField, Typography, useTheme, LinearProgress } from "@mui/material";
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

const NetzbetreiberUpload = () => {
  const navigate = useNavigate();  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [isUploading, setIsUploading] = React.useState(false)
  const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
  const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);
  const [failModalIsOpen2, setFailModalIsOpen2] = React.useState(false);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [haushaltID, setHaushaltID] = React.useState<number>(0)


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

  const sendFile = () => {
    setIsUploading(true);
    const token = localStorage.getItem("accessToken");
    const formData = new FormData();
    if (selectedFile) {
      formData.append("file", selectedFile);
    }
    axios.post(addSuffixToBackendURL("netzbetreiber/dashboard/" + haushaltID), formData, {headers: { Authorization: `Bearer ${token}` }})
    .then((res) => {
      console.log(res.data)
      setSuccessModalIsOpen(true)
    })
    .catch((err) => {
        if (err.response && err.response.status === 404) {
            setFailModalIsOpen2(true)
        }
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
            <TextField
            label="Haushalt ID eingeben"
            type="number"
            variant="outlined"
            //@ts-ignore
            onChange={(e) => {
                setHaushaltID(e.target.value)
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
            </Box>
        </Box>
        <Box component="form"  m="20px" sx={{display: "grid"}}>
            
            <Box sx={{display: "flex", justifyContent: "center", gridColumn: "span 8" , marginTop: "0px"}}>
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
            <Box m="20px" 
            display="grid"
            gridTemplateColumns="repeat(4, 1fr)">
            <Box
            sx={{justifyContent: "center", gridColumn: "span 2" , marginTop: "0px" }}>
                <Box>
            <Typography sx={{display: "grid", justifyContent: "center" , marginTop: "0px", color:"blue", padding: "10px 20px", borderRadius:"5px"
            }} border={`1px solid ${colors.color1[400]}`}> 
            <a href={URL.createObjectURL(selectedFile)} target="_blank" rel="noopener noreferrer">
            {selectedFile.name}
            </a>
            </Typography>
            </Box>
            </Box>
            <Box sx={{justifyContent:"center",  gridColumn: "span 2"}} >
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
        <SuccessModal open={failModalIsOpen2} handleClose={() => setFailModalIsOpen2(false)} 
        text="Haushalt ID exisitiert nicht" />
        <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)}
        text="Daten erfolgreich abgeschickt!" navigationGoal="/netzbetreiber/"/>
    </>
  )
      };


      



    

export default NetzbetreiberUpload;