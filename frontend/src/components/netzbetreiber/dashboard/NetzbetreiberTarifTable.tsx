import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect } from "react";
import Header from "../../utility/Header";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";


const NetzbetreiberTarifTable = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [data, setData] = useState([]);
  const [selectedRowId, setSelectedRowId] = useState(null);
  const navigate = useNavigate();

  const handleRowClick = (params) => {
    navigate("/tarifEdit/" + params.id);
  };
  const handleSelectionChange = (selectionModel) => {
    if (selectionModel.length > 0) {
      const selectedID = selectionModel[0]; // Assuming single selection
      navigate("/netzbetreiber/tarifEdit/" + selectedID);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setData, "netzbetreiber/tarife", navigate,  {Authorization: `Bearer ${token}`})
  }, [])

const columns = [
    {
        field: "tarif_id",
        headerName: "ID",
        flex: 1,
        cellClassName: "name-column--cell",
      },

    {
        field: "tarifname",
        headerName: "Tarifname",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "preis_kwh",
        headerName: "Preis pro kWh",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "grundgebuehr",
        headerName: "Grundgebühr",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "laufzeit",
        headerName: " Laufzeit",
        flex: 1,
      renderCell: ({ row: {laufzeit} }) => {
        return (
          <Box
            width="100%"
            p="5px"
            display="flex"
            justifyContent="center"
            backgroundColor={
              laufzeit < 2
                ? colors.color1[400]
                : laufzeit < 5
                ? colors.color2[500]
                : laufzeit < 10
                ? colors.color4[500]
                : colors.color5[500]
            }
            borderRadius="4px"
          >
            <Typography color={colors.grey[100]} sx={{ ml: "5px" }}>
              {laufzeit}
            </Typography>
          </Box>
        );
      },
    },
    {
      field: "spezielle_konditionen",
      headerName: "Spezielle Konditionen",
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
         <Header title="Tarifübersicht" subtitle="Anzahl der Nutzer pro Nutzergruppe"/>
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
    <DataGrid checkboxSelection getRowId={(row) => row.tarif_id} rows={data} 
    columns={columns} hideFooter={false} onSelectionModelChange={handleSelectionChange} 
    onRowClick={handleRowClick} sx={{cursor: "pointer"}}/>
  </Box>
</Box>
    </Grow>

    </Box>
)

}


export default NetzbetreiberTarifTable;