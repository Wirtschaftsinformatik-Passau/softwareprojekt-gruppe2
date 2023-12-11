import { Box, Typography, useTheme } from "@mui/material";
import Header from "../../utility/Header";
import Grow from "@mui/material/Grow";
import PieChart from "../../utility/visualization/PieChart";



const AdminRoleOverview = () => {

    return (
        
        <Box
        display="grid"
        gridTemplateColumns="repeat(2, 1fr)"
        gridAutoRows="140px"
        gap="0px">
            <Box gridColumn={"span 2"} m="20px">
             <Header title="Rollenübersicht" subtitle="Anzahl der Nutzer pro Nutzergruppe"/>
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
               
                <PieChart isDashboard={false}/>
                 </Box>
        </Grow>

        </Box>
    )

}

export default AdminRoleOverview;