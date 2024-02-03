import { Box, Typography, useTheme } from "@mui/material";
import React from "react";
import { useNavigate } from "react-router-dom";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import Header from "../../utility/Header";
import Grow from "@mui/material/Grow";
import AdminPanelSettingsOutlinedIcon from "@mui/icons-material/AdminPanelSettingsOutlined";
import HomeIcon from '@mui/icons-material/Home';
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PowerIcon from '@mui/icons-material/Power';
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import PieChart from "../../utility/visualization/PieChart";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";

// TypeScript interface for defining the structure of a single pie data item
interface PieDataItem {
  id: string; // Assuming 'id' is a string that represents user roles, e.g., "Admin", "Netzbetreiber"
  value: number; // Number of users in each role
}

// TypeScript interface for defining the structure of the state that holds the pie chart data
interface PieDataState {
  pieData: PieDataItem[];
}

const AdminRoleOverview: React.FC = () => {
  const theme = useTheme(); // Using theme for consistent styling across the app
  const colors = tokens(theme.palette.mode); // Accessing color tokens based on the current theme mode
  const navigate = useNavigate();
  const [pieData, setPieData] = React.useState<PieDataItem[]>([]); // State for storing pie chart data

  // Function to add a unique ID to each item for use as a key in rendering lists
  const addUniqueId = (item: PieDataItem, index: number): PieDataItem & { item_id: string } => {
    return { ...item, item_id: `item-${index}` };
  };


    React.useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setPieData, "admin/userOverview", navigate,  {Authorization: `Bearer ${token}`})
      }, [])

    
      const columns = [
        {
          field: "id",
          headerName: "Nutzerrolle",
          flex: 1,
          renderCell: ({ row: {id} }) => {
            return (
              <Box
                width="100%"
                p="5px"
                display="flex"
                justifyContent="center"
                backgroundColor={
                  id === "Admin"
                    ? colors.color1[400]
                    : id === "Netzbetreiber"
                    ? colors.color2[500]
                    : id === "Energieberatende"
                    ? colors.color3[500]
                    : id === "Solarteure" 
                    ? colors.color4[500]
                    : colors.color5[500]
                }
                borderRadius="4px"
              >
                {id === "Admin" && <AdminPanelSettingsOutlinedIcon />}
                {id === "Netzbetreiber" && <PowerIcon />}
                {id === "Haushalte" && <HomeIcon />}
                {id === "Energieberatende" && <PointOfSaleIcon />}
                {id === "Solarteure" && <SolarPowerIcon />}
                <Typography color={colors.grey[100]} sx={{ ml: "5px" }}>
                  {id}
                </Typography>
              </Box>
            );
          },
        },
        {
          field: "value",
          headerName: "Anzahl Nutzer",
          flex: 1,
          cellClassName: "name-column--cell",
        }
      ];
    return (
        
        <Box
        display="grid"
        gridTemplateColumns="repeat(2, 1fr)"
        gridTemplateRows="repeat(2, 1fr)"
        gridAutoRows="140px"
        gap="0px">
            <Box gridColumn={"span 2"} m="20px">
             <Header title="Rollenübersicht" subtitle="Anzahl der Nutzer pro Nutzergruppe"/>
             </Box>
            
        <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 3"}
            gridColumn={"span 3"} 
            display="flex"
            alignItems="center"
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <PieChart isDashboard={false} data={pieData}/>
                 </Box>
        </Grow>
     
  
            
        <Grow in={true} timeout={1000}>
        <Box ml="10px" borderRadius="20px" gridTemplateColumns={"span-6"} width={"200%"} 
        >
      <Box
        m="0px 0 0 0"
        height="100vh"
        gridColumn={"span-2"}
        sx={{
          "& .MuiDataGrid-root": {
            border: "none",
          },
          "& .MuiDataGrid-cell": {
            color: theme.palette.neutral.light,
            borderBottom: "none",
          },
          "& .name-column--cell": {
            color: theme.palette.neutral.light,
          },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.color1[400],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: theme.palette.background.default,
          },
          "& .MuiDataGrid-footerContainer": {
            borderTop: "none",
            backgroundColor: colors.color1[400],
            color: theme.palette.neutral.light,
          },
          "& .MuiCheckbox-root": {
            color: colors.color1[500],
          },
          "& .MuiSvgIcon-root": {
            color: colors.color1[500],
          },
        }}
      >
        <DataGrid checkboxSelection getRowId={(row) => row.item_id} rows={pieData.map(addUniqueId)} columns={columns} hideFooter={true}/>
      </Box>
    </Box>
        </Grow>

        </Box>
    )

}

export default AdminRoleOverview;