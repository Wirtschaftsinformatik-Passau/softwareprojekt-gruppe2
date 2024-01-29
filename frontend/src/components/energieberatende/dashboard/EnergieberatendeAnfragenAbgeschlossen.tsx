import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect, SetStateAction } from "react";
import Header from "../../utility/Header";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { SolarteurResponse } from "../../../entitities/pv";
import { NoRowsOverlay } from "../../utility/NoRows";
import {ProzessStatus} from "../../../entitities/pv";


const EnergieberatendeAnfragenAbgeschlossen = () => {
  const theme = useTheme();
  const colors: Object = tokens(theme.palette.mode);
  const [data, setData] = useState<SolarteurResponse[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setData, "energieberatende/anfragen?prozess_status=Abgenommen",    
     navigate,  {Authorization: `Bearer ${token}`})
  }, [])

  const handleRowClick = (params: { row: { anlage_id: SetStateAction<number>,
          prozess_status: SetStateAction<ProzessStatus> }; }) => {
    navigate(`/energieberatende/antragTable/${params.row.anlage_id}?status=${params.row.prozess_status}`);
  }



const columns = [
    {
        field: "anlage_id",
        headerName: "ID",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "vorname",
        headerName: "Vorname",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "nachname",
        headerName: "Nachname",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "email",
        headerName: "Email",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "strasse",
        headerName: "Straße",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "hausnummer",
        headerName: "Hausnummer",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "plz",
        headerName: "PLZ",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "stadt",
        headerName: "Stadt",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "prozess_status",
        headerName: "Status",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      }
    
  ];


return (
    
    <Box
    display="grid"
    gridTemplateColumns="repeat(2, 1fr)"
    gridAutoRows="140px"
    gap="0px">
        <Box gridColumn={"span 2"} m="20px">
         <Header title="Abgeschlossene Anträge" subtitle="Antrag auswählen zum bearbeiten"/>
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
    <DataGrid checkboxSelection getRowId={(row) => row.anlage_id} rows={data} 
      columns={columns} hideFooter={false} sx={{cursor: "pointer"}}  onRowClick={handleRowClick}
      localeText={{
        noRowsOverlay: NoRowsOverlay("Keine Anträge vorhanden")
      
      }}
      />
  </Box>
</Box>
    </Grow>

    </Box>
)

}


export default EnergieberatendeAnfragenAbgeschlossen;