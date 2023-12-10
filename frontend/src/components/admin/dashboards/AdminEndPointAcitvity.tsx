import { Box, Typography, useTheme } from "@mui/material";
import Header from "../../utility/Header";
import LineChart from "../../utility/visualization/LineChart";


const AdminEndPointActivity = () => {

    return (
        <Box m="20px">
            <Header title="Endpunkt Aktivität" subtitle="Anzahl der Aufrufe der jeweligen Endpunkt in der vergangenen Zeit"/>
            <Box height={"75vh"}>
               <LineChart />
            </Box>
        </Box>
    )

}

export default AdminEndPointActivity;