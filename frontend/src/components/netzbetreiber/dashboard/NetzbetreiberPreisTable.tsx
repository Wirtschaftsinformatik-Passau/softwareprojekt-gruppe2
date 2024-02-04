import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect } from "react";
import Header from "../../utility/Header";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";


const NetzbetreiberPreisTable = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [data, setData] = useState([]);
  const [selectedRowId, setSelectedRowId] = useState(null);
  const navigate = useNavigate();

  const handleRowClick = (params) => {
    navigate("/preisEdit/" + params.id);
  };
  const handleSelectionChange = (selectionModel) => {
    if (selectionModel.length > 0) {
      const selectedID = selectionModel[0]; // Assuming single selection
      navigate("/netzbetreiber/priceEdit/" + selectedID);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setData, "netzbetreiber/preisstrukturen", navigate,  {Authorization: `Bearer ${token}`})
  }, [])

const columns = [
    {
        field: "preis_id",
        headerName: "ID",
        flex: 1,
        cellClassName: "name-column--cell",
      },

    {
        field: "einspeisung_kwh",
        headerName: "Einspeisepreis pro kWh",
        flex: 1,
        cellClassName: "name-column--cell",
      },   
      {
        field: "bezugspreis_kwh",
        headerName: "Bezugspreis pro kWh",
        flex: 1,
        cellClassName: "name-column--cell",
      }, 
  ];
return (
    
    <Box
    display="grid"
    gridTemplateColumns="repeat(2, 1fr)"
    gridAutoRows="140px"
    gap="0px">
        <Box gridColumn={"span 2"} m="20px">
         <Header title="Preisstrukturübersicht" subtitle="Detailliert Übersicht über Preise. Zum bearbeiten auf Preis klicken."/>
         </Box>

        
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
    <DataGrid checkboxSelection getRowId={(row) => row.preis_id} rows={data} 
    columns={columns} hideFooter={false} onSelectionModelChange={handleSelectionChange} 
    onRowClick={handleRowClick} sx={{cursor: "pointer"}}/>
  </Box>
</Box>
    </Grow>

    </Box>
)

}


export default NetzbetreiberPreisTable;