import { Box, Typography, useTheme } from "@mui/material";
import Header from "../../utility/Header";
import Grow from "@mui/material/Grow";
import { useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import LineChart from "../../utility/visualization/LineChart";
import BarChart from "../../utility/visualization/BarChart";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";


const AdminEndPointActivity = () => {
    const [lineData, setLineData] = useState([]);
    const [barData, setBarData] = useState([]);
    const [successData, setSuccessData] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setLineData, "admin/endpointOverview", navigate,  {Authorization: `Bearer ${token}`})
      }, [])
  
      useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setBarData, "admin/logOverview", navigate,  {Authorization: `Bearer ${token}`})
      }, [])

      useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setSuccessData, "admin/successOverview", navigate,  {Authorization: `Bearer ${token}`})
      } , [])
  

    return (
        <Box>
        <Box
        m="20px"
        display="grid"
        gridTemplateColumns="repeat(2, 1fr)"
        gridAutoRows="140px"
        gap="10px">
        <Box gridColumn={"span 1"} m="20px">
             <Header title="Endpunktaktivität allgemein" subtitle="Anzahl der aufgerufenen Backend Endpunkte"/>
             </Box>
             <Box gridColumn={"span 1"} m="20px">
             <Header title="Endpunktaktivität spezifisch" subtitle="Anzahl der spezifischen Endpunkt Aufrufe und Entwicklung über die Zeit"/>
             </Box>
       
   <Grow in={true} timeout={1000}>
       <Box 
       gridRow={"span 2"}
       gridColumn={"span 1"} 
       display="flex"
       alignItems="center"
     
       borderRadius={"15px"}
       boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
       justifyContent="center">
          
           <BarChart isDashboard={false} data={barData}/>
            </Box>
   </Grow>
   <Grow in={true} timeout={1000}>
       <Box 
       gridRow={"span 2"}
       gridColumn={"span 1"} 
       display="flex"
       alignItems="center"
     
       borderRadius={"15px"}
       boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
       justifyContent="center">
          
           <LineChart isDashboard={false} data={lineData}/>
            </Box>
   </Grow>
   </Box>
   {/*
   <Box
        m="20px"
        display="grid"
        gridTemplateColumns="repeat(2, 1fr)"
        gridAutoRows="140px"
        gap="10px">
        <Box gridColumn={"span 1"} m="20px">
             <Header title="Endpunktaktivität allgemein" subtitle="Anzahl der aufgerufenen Backend Endpunkte"/>
             </Box>
             <Box gridColumn={"span 1"} m="20px">
             </Box>
       
   <Grow in={true} timeout={1000}>
       <Box 
       gridRow={"span 2"}
       gridColumn={"span 1"} 
       display="flex"
       alignItems="center"
     
       borderRadius={"15px"}
       boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
       justifyContent="center">
          
           <BarChart isDashboard={true} data={successData}/>
            </Box>
    </Grow>
   

    </Box> */}
   </Box>
  
        
    )

}

export default AdminEndPointActivity;