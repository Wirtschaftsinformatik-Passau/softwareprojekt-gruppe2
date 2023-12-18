import { Box, Button, TextField } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@material-ui/core";
import {CircularProgress} from "@mui/material";
import React, { useEffect } from "react";
import {Grow} from "@mui/material";
import axios from "axios";

import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import LineChart from "../../utility/visualization/LineChart";
import Header from "../../utility/Header";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { tokens } from "../../../utils/theme";
import SuccessModal from "../../utility/SuccessModal";
import { convertToDateOnly, convertToTimeOnly } from "../../../utils/dateUtils";


interface SmartmeterData {
    datum: string,
    gesamt_pv_erzeugung: number,
    gesamt_soc: number,
    gesamt_batterie_leistung: number,
    gesamt_last: number,
    [key: string]: string | number
}

interface ExtractedFieldData {
    x: string;
    y: number;
}

interface ExtractedData {
    id: string;
    data: ExtractedFieldData[];
}

const extractFieldFromData = (rawData: Array<SmartmeterData>, field: string): ExtractedData[] => {
    const lineData=  rawData.map(item => ({ x: item.datum, y: item[field] as number }))
    console.log(lineData)
    const extracted = [{ 
        id: field, 
        data: lineData
    }];
    return extracted;
};

// todo: smart meter peak daten anzeigen
// am besten als barchart
const NetzbetreiberSmartmeterOverview = () => {
    const navigate = useNavigate();
  
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [haushaltID, setHaushaltID] = React.useState(0)
    const [pvData, setPvData] = React.useState([])
    const [pvPeriod, setPvPeriod] = React.useState("HOUR")
    const [loading, setLoading] = React.useState(false)

    const intervalMapping = {
        "WEEK": 2,
        "MONTH": 1,
        "DAY": 5,
        "HOUR": 80,
        "MINUTE": 1000
    }

    const periodMapping = {
        "WEEK": convertToDateOnly,
        "MONTH": convertToDateOnly,
        "DAY": convertToDateOnly,
        "HOUR": convertToTimeOnly,
        "MINUTE": convertToTimeOnly  
    }

    
   

    // haushalt id checken!!
    // übersicht über haushalte??
    // gibt es nur einen netzbetreiber

    const handleEditButton = () => {
        const token = localStorage.getItem("accessToken");
        setLoading(true)
        axios.get(addSuffixToBackendURL(`netzbetreiber/dashboard/${haushaltID}?field=pv&period=${pvPeriod}`), {headers: { Authorization: `Bearer ${token}` }})
        .then((response) => {
            if(response.status === 200){
                setPvData(response.data)
                setLoading(false)
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
                setLoading(false)
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
              <Button  sx={{background: colors.color1[400],  color: theme.palette.background.default}} variant="contained"
              onClick={handleEditButton}>
                Haushalt auswählen
              </Button>
            </Box>
            </Box>
            {loading ? 
            (<Box display="flex" justifyContent="center" alignItems="center" height="300px">
                    <CircularProgress />
                </Box>) : 
            (<Box
                component="div"
                display="grid"
                gap="30px"
                gridTemplateColumns="repeat(4, minmax(0, 1fr))"
            >
                
                <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 12"}
            gridColumn={"span 2"} 
            display="flex"
            alignItems="center"
            sx={{
              cursor: "pointer",
              ":hover":{
                backgroundColor: colors.grey[800],
              }
            }}
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <LineChart isDashboard={false} data={[{id:"gesamt_pv_erzeugung", data:periodMapping[pvPeriod](pvData)}]} 
                tickInterval={intervalMapping[pvPeriod]} enablePoints={false}/>
                 </Box>
        </Grow>
            
                </Box>)}

            <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
             text="Haushalt ID existiert nicht" />
        </Box>
    )
}

export default NetzbetreiberSmartmeterOverview;