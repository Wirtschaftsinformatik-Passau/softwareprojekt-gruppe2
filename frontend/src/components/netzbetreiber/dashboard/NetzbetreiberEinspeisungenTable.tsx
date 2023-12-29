import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect } from "react";
import AdminPanelSettingsOutlinedIcon from "@mui/icons-material/AdminPanelSettingsOutlined";
import HomeIcon from '@mui/icons-material/Home';
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PowerIcon from '@mui/icons-material/Power';
import SolarPowerIcon from '@mui/icons-material/SolarPower';
import PieChart from "../../utility/visualization/PieChart";
import Header from "../../utility/Header";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";

  
const HaushalteTable = () => {
  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();
  const [haushalte, setHaushalte] = useState([]);


  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get(addSuffixToBackendURL("netzbetreiber/einspeisezusagen"), {headers: { Authorization: `Bearer ${token}` }})
    .then((res) => {
      let users = res.data;
      setHaushalte(users)
    })
    .catch((err) => {
      if (err.response && err.response.status === 401 || err.response.status === 403) {
        console.log("Unauthorized  oder kein Netzbetreiber", err.response.data)
        navigate("/login")
      }
      console.log(err.response.data)
    })
  }, [])


  const columns = [

    { field: "anlage_id", headerName: "Anlage ID" },

    {
      field: "solarteur_id",
      headerName: "Solarteur ID",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
      field: "modultyp",
      headerName: "Modultyp",
      flex: 1,
    },
    {
      field: "kapazitaet",
      headerName: "Kapazität",
      flex: 1,
    },
    {
      field: "installationsflaeche",
      headerName: "Installationsfläche",
      flex: 1,
    },
    {
        field: "prozess_status",
        headerName: "Prozess Status",
        flex: 1,
    },
    {
        field: "nvpruefung_status",
        headerName: "Netzbetreiberprüfung Status",
        flex: 1,
    },
  ];

  const handleRowClick = (params: { id: string; }) => {
    navigate("/netzbetreiber/einspeisungenZusage/" + params.anlage_id);
  };
  const handleSelectionChange = (selectionModel: string | any[]) => {
    if (selectionModel.length > 0) {
      const selectedID = selectionModel[0]; // Assuming single selection
      navigate("/netzbetreiber/einspeisungenZusage/" + selectedID);
    }
  };
  return (
    <Box m="20px">
      <Header title="Offene Einspeisungen" subtitle="Offene Anträge welche angenommen werden können"/>
      <Box
        m="40px 0 0 0"
        height="75vh"
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
        <DataGrid checkboxSelection getRowId={(row) => row.anlage_id} rows={haushalte} columns={columns} 
        sx={{
          cursor: "pointer",
        }}  onSelectionModelChange={handleSelectionChange} 
        onRowClick={handleRowClick} />
      </Box>
    </Box>
  );
};

export default HaushalteTable;