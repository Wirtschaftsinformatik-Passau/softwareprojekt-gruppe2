import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { useState, useEffect, SetStateAction } from "react";
import Header from "../../utility/Header";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import {Zahlungsstatus, Rechnung} from "../../../entitities/pv";


const EnergieberaterRechnungsTable = () => {
    const theme = useTheme();
    const colors: Object = tokens(theme.palette.mode);
    const [data, setData] = useState<Rechnung[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setData, "haushalte/rechnungen?rolle=steller", navigate,  {Authorization: `Bearer ${token}`})
    }, [])

   


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


    return (

        <Box
            display="grid"
            gridTemplateColumns="repeat(2, 1fr)"
            gridAutoRows="140px"
            gap="0px">
            <Box gridColumn={"span 2"} m="20px">
                <Header title="Rechnungsübersicht" subtitle="Übersicht über alle gestellten Rechnungen"/>
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
                                  columns={columns} hideFooter={false} sx={{cursor: "pointer"}}/>
                    </Box>
                </Box>
            </Grow>

        </Box>
    )

}


export default EnergieberaterRechnungsTable;