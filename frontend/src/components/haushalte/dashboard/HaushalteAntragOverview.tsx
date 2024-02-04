import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../utils/theme";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { useState, useEffect, SetStateAction } from "react";
import Header from "../../utility/Header";
import { useNavigate } from "react-router-dom";
import {Grow} from "@mui/material";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import CheckIcon from '@mui/icons-material/Check';
import { PVAntrag } from "../../../entitities/pv";
import { getAllReports, ReportURL } from "../../../utils/download_utils";


// todo: conditional rendering of navigation of table based on prozesstatus

const HaushaltAntragTable = () => {
  const theme = useTheme();
  const colors: Object = tokens(theme.palette.mode);
  const [data, setData] = useState<PVAntrag[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setData, "haushalte/angebot-anfordern", navigate,  {Authorization: `Bearer ${token}`})
  }, [])

  const handleRowClick = (params: { row: { anlage_id: SetStateAction<number> ,
                                          prozess_status: SetStateAction<String>}; }) => {
    const { row } = params;
    console.log(row)
    switch (row.prozess_status) {
    case "DatenAngefordert":  navigate("/haushalte/dataOverview/")
    break;
    case "AngebotGemacht":  navigate("/haushalte/angebote/"+row.anlage_id)
    break;
    case "PlanErstellt" : {
      const InstallationsPlanUrl: ReportURL= {
        endpoint: "solarteure/installationsplan/" + row.anlage_id,
        filename: `installationsplan_${row.anlage_id}.csv`,
      }
      const plans: ReportURL[] = new Array(InstallationsPlanUrl)
      getAllReports(plans)
    }
    break;
    default: undefined
    
  }
}

  
//todo: genauere Erklärung
  const prozessStatusErklaerung = [
   ["AnfrageGestellt", "Anfrage wurde gestellt", ""],
    ["DatenAngefordert", "Daten wurden angefordert", <CheckIcon/>],
    ["DatenFreigegeben", "Daten wurden freigegeben", ""],
    ["AngebotGemacht", "Angebot wurde gemacht", <CheckIcon/>],
    ["AngebotAngenommen", "Angebot wurde angenommen", ""],
    ["PlanErstellt", "Plan wurde erstellt", "Download des Plans möglich durch Klicken"],
    ["Genehmigt", "Plan wurde genehmigt", ""],
    ["Abgenommen", "Plan wurde abgenommen", ""],
    ["InstallationAbgeschlossen", "Installation wurde abgeschlossen", ""],
  ]


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
        field: "netzbetreiber_id",
        headerAlign: "left",
        align: "left",
        headerName: "Netzbetreiber ID",
        flex: 1,
        cellClassName: "name-column--cell",
      },

    {
        field: "solarteur_id",
        headerAlign: "left",
        align: "left",
        headerName: "Solarteur ID",
        flex: 1,
        cellClassName: "name-column--cell",
      },
      {
        field: "prozess_status",
        headerAlign: "left",
        align: "left",
        headerName: "Prozess Status",
        flex: 1,
        cellClassName: "name-column--cell",
        renderCell: ({ row: {prozess_status} }) => {
            return (
              <Box
              width="100%"
              p="5px"
              display="flex"
              justifyContent="center"
              backgroundColor={
                prozess_status === "DatenAngefordert"
                  ? colors.color5[400] :
                  prozess_status === "AngebotGemacht"
                  ? colors.color3[400] :
                  prozess_status === "PlanErstellt"
                  ? colors.color4[400] :
                   undefined}
            >
              <Typography color={colors.grey[100]} sx={{ ml: "5px" }}>
                {prozess_status}
              </Typography>
            </Box>
            );
          },
      },
      {
        field: "nvpruefung_status",
        headerAlign: "left",
        align: "left",
        headerName: " Prüfung erfolgreich",
        type: "number",
        flex: 1,
        cellClassName: "name-column--cell"
    },
    
  ];
return (
    
    <Box
    display="grid"
    gridTemplateColumns="repeat(2, 1fr)"
    gridAutoRows="auto"
    gap="0px">
        <Box gridColumn={"span 2"} mt="20px">
         <Header title="Antragsübersicht" subtitle="Übersicht über alle gestellten Anträge" mb="5px"/>
         </Box>
         
  

        
    <Grow in={true} timeout={1000}>
    <Box ml="10px" borderRadius="20px" gridTemplateColumns={"span-6"} width={"200%"} borderBottom={`2px solid ${colors.color2[100]}`}
    >
  <Box
    m="0px 0 0 0"
    
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
    <DataGrid checkboxSelection getRowId={(row) => row.anlage_id} rows={data} autoHeight 
    columns={columns} hideFooter={true} sx={{cursor: "pointer"}} onRowClick={handleRowClick}/>
  </Box>
</Box>
    </Grow>
    <Grow in={true} timeout={1000}>
    <Box gridColumn={"span 2"} display={"grid"} justifyContent={"center"} gridTemplateColumns="repeat(2, 1fr)" mt="20px" >
          <Box textAlign={"center"} gridColumn={"span 2"} >
        <Header title="Erklärung Prozessstatus" variant="h3" mb="10px" subtitle="Wenn Handlung nötig, dann bitte auf Antrag in Tabelle klicken und bearbeiten"/>
        </Box>

        <Box display={"flex"} justifyContent={"center"} gridColumn={"span 2"} mb={"10px"} mt="10px" ml="10px"
        sx = {{
          "& .MuiTableCell-root": {
            color: colors.color1[400],
            fontSize: "0.9rem",
          },
          "& .MuiTableCell-head": {
            fontWeight: "bold",
          },
        }}>
        <TableContainer component={Paper} >
      <Table  sx={{ minWidth: 60, backgroundColor: theme.palette.background.default, color: colors.color1[400] }} aria-label="simple table"> 
        <TableHead>
          <TableRow>
            <TableCell align="center">Eintrag</TableCell>
            <TableCell align="center">Beschreibung</TableCell>
            <TableCell align="center">Handlung nötig?</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {prozessStatusErklaerung.map((row) => (
            <TableRow
              key={row[0]}
              sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
            >
              <TableCell align="center" component="th" scope="row">
                {row[0]}
              </TableCell>
              <TableCell align="center">{row[1]}</TableCell>
              <TableCell align="center">{row[2]}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
        </Box>
    </Box>
    </Grow>
    </Box>
)

}


export default HaushaltAntragTable;