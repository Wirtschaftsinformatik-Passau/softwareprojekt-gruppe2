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

const mockusers = [
    {
        "nachname": "test",
        "email": "1234@1234.de",
        "vorname": "tst",
        "rolle": null,
        "adresse_id": 4,
        "geburtsdatum": "2000-01-22",
        "user_id": 1,
        "passwort": "12345",
        "telefonnummer": "010120220"
    },
    {
        "nachname": "test",
        "email": "1234@1234.de",
        "vorname": "tst",
        "rolle": null,
        "adresse_id": 4,
        "geburtsdatum": "2000-01-22",
        "user_id": 2,
        "passwort": "12345",
        "telefonnummer": "010120220"
    },
    {
        "nachname": "test",
        "email": "1234@1234.de",
        "vorname": "tst",
        "rolle": null,
        "adresse_id": 4,
        "geburtsdatum": "2000-01-22",
        "user_id": 3,
        "passwort": "12345",
        "telefonnummer": "010120220"
    },
    {
        "nachname": "test",
        "email": "1234@1234.de",
        "vorname": "tst",
        "rolle": null,
        "adresse_id": 4,
        "geburtsdatum": "2000-01-22",
        "user_id": 4,
        "passwort": "12345",
        "telefonnummer": "010120220"
    },
    {
        "nachname": "test",
        "email": "1234@1234.dee",
        "vorname": "tst",
        "rolle": null,
        "adresse_id": 4,
        "geburtsdatum": "2000-01-22",
        "user_id": 9,
        "passwort": "12345",
        "telefonnummer": "010120220"
    },
    {
        "nachname": "dd",
        "email": "123@wreb.de",
        "vorname": "dd",
        "rolle": "Admin",
        "adresse_id": 16,
        "geburtsdatum": "1993-07-28",
        "user_id": 10,
        "passwort": "123",
        "telefonnummer": "1"
    },
    {
        "nachname": "dd",
        "email": "123@web.de",
        "vorname": "dd",
        "rolle": "Admin",
        "adresse_id": 19,
        "geburtsdatum": "2023-11-27",
        "user_id": 11,
        "passwort": "123",
        "telefonnummer": "123"
    },
    {
        "nachname": "123",
        "email": "1232343233@web.de",
        "vorname": "123",
        "rolle": "Netzbetreiber",
        "adresse_id": 24,
        "geburtsdatum": "2023-11-29",
        "user_id": 12,
        "passwort": "123",
        "telefonnummer": "123"
    },
    {
        "nachname": "dd",
        "email": "123456@wreb.de",
        "vorname": "dd",
        "rolle": "Admin",
        "adresse_id": 16,
        "geburtsdatum": "1993-07-28",
        "user_id": 13,
        "passwort": "123",
        "telefonnummer": "1"
    },
    {
        "nachname": "dd",
        "email": "123ddfffff@web.de",
        "vorname": "dd",
        "rolle": "Admin",
        "adresse_id": 28,
        "geburtsdatum": "2023-11-26",
        "user_id": 14,
        "passwort": "123",
        "telefonnummer": "123"
    },
    {
        "nachname": "dd",
        "email": "1@1.de",
        "vorname": "dd",
        "rolle": "Admin",
        "adresse_id": 16,
        "geburtsdatum": "1004-07-28",
        "user_id": 15,
        "passwort": "123",
        "telefonnummer": "1"
    },
    {
        "nachname": "dd",
        "email": "1@2.de",
        "vorname": "dd",
        "rolle": "Admin",
        "adresse_id": 16,
        "geburtsdatum": "1004-07-28",
        "user_id": 16,
        "passwort": "$2b$12$yPz.5Jki3DbeiZecWrjTp.PsHC3mITyTR0p2.4mcy48B9.8EsV/Dq",
        "telefonnummer": "1"
    }]

  
const UserTable = () => {
  
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);

  const handleRowClick = (params) => {
    navigate("/admin/editUser" + params.id);
  };
  const handleSelectionChange = (selectionModel) => {
    if (selectionModel.length > 0) {
      const selectedID = selectionModel[0]; // Assuming single selection
      navigate("/admin/editUser/" + selectedID);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get(addSuffixToBackendURL("users"), {headers: { Authorization: `Bearer ${token}` }})
    .then((res) => {
      let users = res.data;
      setUsers(users)
    })
    .catch((err) => {
      if (err.response && err.response.status === 401 || err.response.status === 403) {
        console.log("Unauthorized  oder kein Admin", err.response.data)
        navigate("/login")
      }
      console.log(err.response.data)
    })
  
  }, [])

  console.log(users)

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
      field: "rolle",
      headerName: "Nutzerrolle",
      flex: 1,
      renderCell: ({ row: {rolle} }) => {
        return (
          <Box
          width="100%"
          p="5px"
          display="flex"
          justifyContent="center"
          backgroundColor={
            rolle === "Admin"
              ? colors.color1[400]
              : rolle === "Netzbetreiber"
              ? colors.color2[500]
              : rolle === "Energieberatende"
              ? colors.color3[500]
              : rolle === "Solarteure" 
              ? colors.color4[500]
              : colors.color5[500]
          }
          borderRadius="4px"
        >
          {rolle === "Admin" && <AdminPanelSettingsOutlinedIcon />}
          {rolle === "Netzbetreiber" && <PowerIcon />}
          {rolle === "Haushalte" && <HomeIcon />}
          {rolle === "Energieberatende" && <PointOfSaleIcon />}
          {rolle === "Solarteure" && <SolarPowerIcon />}
          <Typography color={colors.grey[100]} sx={{ ml: "5px" }}>
            {rolle}
          </Typography>
        </Box>
        );
      },
    },
  ];

  return (
    <Box m="20px">
      <Header title="Nutzerverwaltung" subtitle="Übersicht über alle registrierten Nutzer"/>
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
        <DataGrid checkboxSelection getRowId={(row) => row.user_id} rows={users} columns={columns} 
        onRowClick={handleRowClick} onSelectionModelChange={handleSelectionChange}
        sx={{
          cursor: "pointer",
        }}/>
      </Box>
    </Box>
  );
};

export default UserTable;