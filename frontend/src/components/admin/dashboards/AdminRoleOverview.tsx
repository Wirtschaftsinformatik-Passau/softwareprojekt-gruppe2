import { Box, Typography, useTheme } from "@mui/material";
import Header from "../../utility/Header";
import PieChart from "../../utility/visualization/PieChart";



const AdminRoleOverview = () => {

    return (
        <Box m="20px">
            <Header title="Nutzerübersicht" subtitle="Übersicht über die Anzahl der Nutzer pro Rolle"/>
            <Box height={"75vh"}>
               <PieChart />
            </Box>
        </Box>
    )

}

export default AdminRoleOverview;