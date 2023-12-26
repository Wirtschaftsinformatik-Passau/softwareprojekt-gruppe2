import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect } from "react";
import Header from "../../utility/Header";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";

export interface Vertrag {
  "vertrag_id": number,
  "user_id": number,
  "tarif_id":  number,
  "beginn_datum": string,
  "end_datum": string,
  "jahresabschlag": number,
  "vertragstatus": boolean
  "tarifname": string,
  "preis_kwh": number,
  "grundgebuehr": number,
  "laufzeit": number,
  "spezielle_konditionen": string,
}

const VertragTable = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [data, setData] = useState<Vertrag[]>([{
    "vertrag_id": 0,
    "user_id": 0,
    "tarif_id":  0,
    "beginn_datum": "",
    "end_datum": "",
    "jahresabschlag": 0,
    "vertragstatus": false,
    "tarifname": "",
    "preis_kwh": 0,
    "grundgebuehr": 0,
    "laufzeit": 0,
    "spezielle_konditionen": ""
  }]);

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setData, "haushalte/vertraege", navigate,  {Authorization: `Bearer ${token}`})
  }, [])



const columns = [
    {
        field: "vertrag_id",
        headerName: "ID",
        flex: 1,
        align: "left",
        headerAlign: "left",
        cellClassName: "name-column--cell",
      },
      {
        field: "netzbetreiber_id",
        headerAlign: "left",
        align: "left",
        headerName: "Netzbetreiber ID",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "beginn_datum",
        headerAlign: "left",
        align: "left",
        headerName: "Beginn Datum",
        flex: 1,
      },
      {
        field: "end_datum",
        headerAlign: "left",
        align: "left",
        headerName: "End Datum",
        flex: 1,
      },
      {
        field: "jahresabschlag",
        headerAlign: "left",
        align: "left",
        headerName: "Jahresabschlag",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "vertragstatus",
        headerAlign: "left",
        align: "left",
        headerName: "Vertragstatus",
        flex: 1,
        cellClassName: "name-column--cell",
      },

    {
        field: "tarifname",
        headerAlign: "left",
        align: "left",
        headerName: "Tarifname",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "preis_kwh",
        headerAlign: "left",
        align: "left",
        headerName: "Preis pro kWh",
        type: "number",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "grundgebuehr",
        headerAlign: "left",
        align: "left",
        headerName: "Grundgebühr",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "laufzeit",
        headerAlign: "left",
        align: "left",
        headerName: " Laufzeit",
        type: "number",
        flex: 1,
        cellClassName: "name-column--cell"
    },
    
  ];
return (
    
    <Box
    display="grid"
    gridTemplateColumns="repeat(2, 1fr)"
    gridAutoRows="140px"
    gap="0px">
        <Box gridColumn={"span 2"} m="20px">
         <Header title="Tarifübersicht" subtitle="Für Details auf Vertrag klicken"/>
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
    <DataGrid checkboxSelection getRowId={(row) => row.vertrag_id} rows={data} 
    columns={columns} hideFooter={false} sx={{cursor: "pointer"}}/>
  </Box>
</Box>
    </Grow>

    </Box>
)

}


export default VertragTable;