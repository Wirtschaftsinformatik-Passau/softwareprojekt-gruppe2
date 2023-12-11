import { Box, Typography, useTheme } from "@mui/material";
import Header from "../../utility/Header";
import Grow from "@mui/material/Grow";
import LineChart from "../../utility/visualization/LineChart";
import BarChart from "../../utility/visualization/BarChart";


const AdminEndPointActivity = () => {

    return (
        <Box
        m="20px"
        display="grid"
        gridTemplateColumns="repeat(2, 1fr)"
        gridAutoRows="140px"
        gap="10px">
        <Box gridColumn={"span 2"} m="20px">
             <Header title="Endpunktaktivität allgemein" subtitle="Anzahl der aufgerufenen Backend Endpunkte"/>
             </Box>
       
   <Grow in={true} timeout={1000}>
       <Box 
       gridRow={"span 3"}
       gridColumn={"span 6"} 
       display="flex"
       alignItems="center"
     
       borderRadius={"15px"}
       boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
       justifyContent="center">
          
           <BarChart isDashboard={false}/>
            </Box>
   </Grow>
   <Box gridColumn={"span 2"} m="20px">
             <Header title="Endpunktaktivität spezifisch" subtitle="Anzahl der spezifischen Endpunkt Aufrufe und Entwicklung über die Zeit"/>
             </Box>
   <Grow in={true} timeout={1000}>
       <Box 
       gridRow={"span 3"}
       gridColumn={"span 6"} 
       display="flex"
       alignItems="center"
     
       borderRadius={"15px"}
       boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
       justifyContent="center">
          
           <LineChart isDashboard={false}/>
            </Box>
   </Grow>

   </Box>
        
  
        
    )

}

export default AdminEndPointActivity;