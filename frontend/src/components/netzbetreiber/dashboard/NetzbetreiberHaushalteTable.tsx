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

  
const NetzbetreiberHaushalteTable = () => {
  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();
  const [haushalte, setHaushalte] = useState([]);


  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get(addSuffixToBackendURL("netzbetreiber/haushalte"), {headers: { Authorization: `Bearer ${token}` }})
    .then((res) => {
      let users = res.data;
      setHaushalte(users)
    })
    .catch((err) => {
      if (err.response && err.response.status === 401 || err.response.status === 403) {
        console.log("Unauthorized  oder kein Admin", err.response.data)
        navigate("/login")
      }
      console.log(err.response.data)
    })
  }, [])



  const columns = [
    { field: "user_id", headerName: "ID" },
    {
      field: "vorname",
      headerName: "Vorname",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
      field: "nachname",
      headerName: "Nachname",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
      field: "email",
      headerName: "E-Mail",
      flex: 1,
    },
    {
      field: "telefonnummer",
      headerName: "Telefonnummer",
      flex: 1,
    },
    {
      field: "geburtsdatum",
      headerName: "Geburtsdatum",
      flex: 1,
    },
    {
        field: "strasse",
        headerName: "Straße",
        flex: 1,
    },
    {
        field: "hausnummer",
        headerName: "Hausnummer",
        flex: 1,
    },
    {
        field: "plz",
        headerName: "PLZ",
        flex: 1,
    },
    {
        field: "stadt",
        headerName: "Ort",
        flex: 1,
    },
  ];

  return (
    <Box m="20px">
      <Header title="Haushaltübersicht" subtitle="Übersicht über alle Haushalte"/>
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
        <DataGrid checkboxSelection getRowId={(row) => row.user_id} rows={haushalte} columns={columns} 
        sx={{
          cursor: "pointer",
        }}/>
      </Box>
    </Box>
  );
};

export default NetzbetreiberHaushalteTable;