import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect, SetStateAction } from "react";
import Header from "../../utility/Header";
import { saveAs } from 'file-saver';
import {Button} from "@mui/material";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import {Zahlungsstatus, Rechnung} from "../../../entitities/pv";
import { convertToCSV } from "../../../utils/download_utils";


const HaushalteRechnungsTable = () => {
    const theme = useTheme();
    const colors: Object = tokens(theme.palette.mode);
    const [data, setData] = useState<Rechnung[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setData, "haushalte/rechnungen?rolle=empfaenger", navigate,  {Authorization: `Bearer ${token}`})
    }, [])

    const handleRowClick = (params: { row: { rechnung_id: SetStateAction<Number>; }; }) => {
        navigate(`/haushalte/rechnungenDetail/${params.row.rechnung_id}`);
    }


    const columns = [
        {
            field: "rechnung_id",
            headerName: "ID",
            flex: 1,
            align: "left",
            headerAlign: "left",
            cellClassName: "name-column--cell",
        },

        {
            field: "rechnungsbetrag",
            headerAlign: "left",
            align: "left",
            headerName: "Rechnungsbetrag",
            flex: 1,
            cellClassName: "name-column--cell",
        },
        {
            field: "rechnungsdatum",
            headerAlign: "left",
            align: "left",
            headerName: "Rechnungsdatum",
            type: "number",
            flex: 1,
            cellClassName: "name-column--cell",
        },
        {
            field: "faelligkeitsdatum",
            headerAlign: "left",
            align: "left",
            headerName: "Fälligkeitsdatum",
            flex: 1,
            cellClassName: "name-column--cell",
        },
        {
            field: "rechnungsart",
            headerAlign: "left",
            align: "left",
            headerName: "Rechnungsart",
            type: "number",
            flex: 1,
            cellClassName: "name-column--cell"
        },
        {
            field: "zahlungsstatus",
            headerAlign: "left",
            align: "left",
            headerName: "Zahlungsstatus",
            flex: 1,
            cellClassName: "name-column--cell",
            renderCell: (params: { value: any; }) => {
                return (
                    <Box
                        width="100%"
                        p="5px"
                        display="flex"
                        justifyContent="center"
                        backgroundColor={
                            params.value === Zahlungsstatus.Bezahlt
                                ? colors.color1[400]
                                : params.value === Zahlungsstatus.Offen
                                ? colors.color4[500]
                                : params.value === Zahlungsstatus.Überfällig
                                ? colors.color5[500]
                                : params.value === Zahlungsstatus.Teilweise_Bezahlt
                                ? colors.color2[500]
                                : undefined
                        }
                        borderRadius="4px"
                        color={theme.palette.neutral.light}
                    >
                        <Typography variant="body2">{params.value}</Typography>
                    </Box>
                );
            }
        },

    ];

    const downloadCSV = (data: Rechnung[] ) => {
        const today = new Date();
        const csvData = convertToCSV(data);
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
        const fileName = `rechnungen_${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}.csv`;
        saveAs(blob, fileName);
    };

    return (

        <Box
            display="grid"
            gridTemplateColumns="repeat(2, 1fr)"
            gridAutoRows="140px"
            gap="40px">
                <Box  gridColumn={"span 2"}>
            <Box m="20px"  >
                <Header title="Rechnungsübersicht" subtitle="Zum bezahlen auf Rechnung klicken"/>
            </Box>
            <Box marginLeft={"85%"}>
                <Button
              onClick={() => downloadCSV(data)}
            sx={{
              backgroundColor: colors.color1[400],
              color: theme.palette.background.default,
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
              ":hover" : {
                backgroundColor: colors.grey[500],
              
              },
    
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Daten herunterladen
          </Button>
          </Box>
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
                        <DataGrid checkboxSelection getRowId={(row) => row.rechnung_id} rows={data}
                                  columns={columns} hideFooter={false} sx={{cursor: "pointer"}} onRowClick={handleRowClick}/>
                    </Box>
                </Box>
            </Grow>

        </Box>
    )

}


export default HaushalteRechnungsTable;