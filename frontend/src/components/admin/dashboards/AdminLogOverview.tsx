import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect } from "react";
import ErrorIcon from '@mui/icons-material/Error';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import { useNavigate } from "react-router-dom";
import {setStateOtherwiseRedirect}  from "../../../utils/stateUtils.js"
import Header from "../../utility/Header";



// TypeScript interface for defining the structure of a log object
interface Log {
  log_id: number;
  timestamp: string;
  level: string;
  name: string;
  message: string;
  user_id: number;
  endpoint: string;
  method: string;
  success: boolean;
}

// TypeScript interface for defining the structure of the state that holds the logs
interface LogsState {
  logs: Log[];
}

const LogOverview = () => {
  const theme = useTheme(); // Use the theme for consistent styling across the app
  const colors = tokens(theme.palette.mode); // Accessing color tokens based on the current theme mode
  const navigate = useNavigate(); // Hook for programmatically navigating between routes
  const [logs, setLogs] = useState<LogsState>({"logs":[{
    "log_id": 0,
    "timestamp": "2023-12-11 23:10:31,122",
    "level": "INFO",
    "name": "GreenEcoHub",
    "message": "User eingeloggt",
    "user_id": 6,
    "endpoint": "/auth/login",
    "method": "POST",
    "success": true
  }]});

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setLogs, "admin/logs", navigate,  {Authorization: `Bearer ${token}`})
  }, [])
 

  const columns = [
    { field: "log_id", headerName: "ID" },
    {
      field: "timestamp",
      headerName: "Zeit",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
        field: "level",
        headerName: "Level",
        flex: 1,
        renderCell: ({ row: {level} }) => {
          return (
            <Box
              width="100%"
              p="5px"
              display="flex"
              justifyContent="center"
              backgroundColor={
                level === "INFO" ? colors.color2[400] : colors.color5[400]
              }
              borderRadius="4px"
            >
              {level === "INFO" && <CheckBoxIcon/>}
              {level === "ERROR" && <ErrorIcon />}
              <Typography color={colors.grey[100]} sx={{ ml: "5px" }}>
                {level}
              </Typography>
            </Box>
          );
        },
      },
    {
      field: "message",
      headerName: "Nachricht",
      flex: 1,
    },
    {
      field: "user_id",
      headerName: "Nutzer ID",
      flex: 1,
    },
    {
      field: "endpoint",
      headerName: "Endpunkt",
      flex: 1,
    },
    {
        field: "method",
        headerName: "Methode",
        flex: 1,
      },
    
  ];

  return (
    <Box m="20px">
      <Header title="Log Aktivität" subtitle="Übersicht das gesamte Logging"/>
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
        <DataGrid checkboxSelection getRowId={(row) => row.log_id} rows={logs} columns={columns} />
      </Box>
    </Box>
  );
};

export default LogOverview;