import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import { useEffect } from "react";
import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import Header from "../../utility/Header";
import {setStateOtherwiseRedirect}  from "../../../utils/stateUtils.js"
import { addSuffixToBackendURL } from "../../../utils/networking_utils";


const NetzHome = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const colors = tokens(theme.palette.mode);
   

    return (
        <Box m="20px">
            <Header title="Netzbetreiber Dashboard" subtitle="Für Details die Reiter in der Sidebar auswählen"/>
            <Box display="flex" justifyContent="end" alignItems="center" >
          <Button
            sx={{
              backgroundColor: colors.color1[400],
              color: theme.palette.background.default,
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
              ":hover" : {
                backgroundColor: colors.grey[500],
              
              }
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Download Reports
          </Button>
        </Box>       
  
        </Box>
        


    
    )
}

export default NetzHome;