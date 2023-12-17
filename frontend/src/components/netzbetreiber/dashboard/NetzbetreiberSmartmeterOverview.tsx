import { Box, Button, TextField } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@material-ui/core";
import CircularProgress from "@mui/material";
import React from "react";
import axios from "axios";

import LineChart from "../../utility/visualization/LineChart";
import Header from "../../utility/Header";
import { tokens } from "../../../utils/theme";
import SuccessModal from "../../utility/SuccessModal";


interface SmartmeterData {
    datum: string,
    gesamt_pv_erzeugung: number,
    gesamt_soc: number,
    gesamt_batterie_leistung: number,
    gesamt_last: number,
    [key: string]: string | number
}

const extractFieldFromData = (data: Array<SmartmeterData>, field: string) => {
    return data.map(item => item[field])
}


const NetzbetreiberSmartmeterOverview = () => {
    const navigate = useNavigate();
  
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [haushaltID, setHaushaltID] = React.useState(0)
    const [data, setData] = React.useState([])

    // haushalt id checken!!
    // übersicht über haushalte??
    // gibt es nur einen netzbetreiber

    const handleEditButton = () => {
        const token = localStorage.getItem("accessToken");
        axios.get("netzbetreiber/smartmeter/"+haushaltID, {headers: { Authorization: `Bearer ${token}` }})
        .then((response) => {
            if(response.status === 200){
                setData(response.data)
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
        <Box m="20px">
            <Header title="Smartmeter" subtitle="Übersicht über Smartmeter Daten für einen Haushalt"/>
            <Box component="form"  m="20px" sx={{display: "grid"}}>
            <TextField
            label="Haushalt ID eingeben"
            type="number"
            onChange={(e) => {setHaushaltID(Number(e.target.value))}}
            variant="outlined"
     
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
           <Box display="flex" justifyContent="end" mt="20px" gridColumn= "span 4">
              <Button type="submit" sx={{background: colors.color1[400],  color: theme.palette.background.default}} variant="contained">
                Haushalt auswählen
              </Button>
            </Box>
            </Box>
            <Box
                component="div"
                display="grid"
                gap="30px"
                gridTemplateColumns="repeat(4, minmax(0, 1fr))"
            >
                <Box gridColumn={"span 2"}>
                    <LineChart/>
                </Box>
            
                </Box>
            <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
             text="Haushalt ID existiert nicht" />
        </Box>
    )
}

export default NetzbetreiberSmartmeterOverview;