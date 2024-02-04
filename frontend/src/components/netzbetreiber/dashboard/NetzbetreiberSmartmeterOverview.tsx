import { Box, Button, TextField, Menu, MenuItem, FormControl, Select, InputLabel } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@material-ui/core";
import {CircularProgress} from "@mui/material";
import { DateRangePicker, DateRange } from "mui-daterange-picker";
import React, {Dispatch, useEffect} from "react";
import {Grow} from "@mui/material";
import axios from "axios";
import { saveAs } from 'file-saver';
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";
import LineChart from "../../utility/visualization/LineChart";
import Header from "../../utility/Header";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import { tokens } from "../../../utils/theme";
import SuccessModal from "../../utility/SuccessModal";
import {convertToDateOnly, convertToTimeOnly, dateFormater, formatDate} from "../../../utils/dateUtils";
import {DataGrid} from "@mui/x-data-grid";
import { convertToCSV } from "../../../utils/download_utils";



export interface SmartmeterData {
    datum: string,
    gesamt_pv_erzeugung: number,
    gesamt_soc: number,
    gesamt_batterie_leistung: number,
    gesamt_last: number,
    [key: string]: string | number
}

interface ExtractedFieldData {
    x: string;
    y: number;
}

interface ExtractedData {
    id: string;
    data: ExtractedFieldData[];
}

enum Period {
    WEEK = "Woche",
    MONTH = "Monat",
    DAY = "Tag",
    HOUR = "Stunde",
    MINUTE = "Minute"

}

const enumPeriodMapping = {
    "Woche": "WEEK",
    "Monat": "MONTH",
    "Tag": "DAY",
    "Stunde": "HOUR",
    "Minute": "MINUTE"
}

const reverseEnumPeriodMapping = {
    "WEEK": "Woche",
    "MONTH": "Monat",
    "DAY": "Tag",
    "HOUR": "Stunde",
    "MINUTE": "Minute"
}


const extractFieldFromData = (rawData: Array<SmartmeterData>, field: string): ExtractedData[] => {
    const lineData=  rawData.map(item => ({ x: item.datum, y: item[field] as number }))
    console.log(lineData)
    const extracted = [{ 
        id: field, 
        data: lineData
    }];
    return extracted;
};


// todo: smart meter peak daten anzeigen
// am besten als barchart
const NetzbetreiberSmartmeterOverview = () => {
    const navigate = useNavigate();
  
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [failModalIsOpen, setFailModalIsOpen] = React.useState(false);
    const [haushaltID, setHaushaltID] = React.useState(0)
    const [pvData, setPvData] = React.useState<ExtractedFieldData[]>([])
    const [socData, setSocData] = React.useState<ExtractedFieldData[]>([])
    const [batterieData, setBatterieData] = React.useState<ExtractedFieldData[]>([])
    const [smartMeterData, setSmartMeterData] = React.useState<SmartmeterData[]>([])
    const [lastData, setLastData] = React.useState<ExtractedFieldData[]>([])
    const [pvPeriod, setPvPeriod] = React.useState<string>("DAY")
    const [loading, setLoading] = React.useState<boolean>(false)
    const [loading1, setLoading1] = React.useState<boolean>(false)
    const [loading2, setLoading2] = React.useState<boolean>(false)
    const [loading3, setLoading3] = React.useState<boolean>(false)
    const [openDateRangePicker, setOpenDateRangePicker] = React.useState(false);
    const [dateRange, setDateRange] = React.useState<DateRange>({ 
        startDate: new Date('2023-01-01'), 
        endDate: new Date('2023-01-30') 
    });

        const toggleDateRangePicker = () => {
            setOpenDateRangePicker(!openDateRangePicker);
          };


    const intervalMapping = {
        "WEEK": 2,
        "MONTH": 1,
        "DAY": 4,
        "HOUR": 2,
        "MINUTE": 60
    }

    const periodMapping = {
        "WEEK": convertToDateOnly,
        "MONTH": convertToDateOnly,
        "DAY": convertToDateOnly,
        "HOUR": convertToTimeOnly,
        "MINUTE": convertToTimeOnly  
    }

    const columns = [
        {
            field: "datum",
            headerName: "Datum",
            flex: 1,
            align: "left",
            headerAlign: "left",
            cellClassName: "name-column--cell",
            renderCell: (params: any) => (
                dateFormater(params.value, true)
            ),
        },
        {
            field: "gesamt_pv_erzeugung",
            headerAlign: "left",
            align: "left",
            headerName: "Gesamt PV Erzeugung Watt",
            flex: 1,
            cellClassName: "name-column--cell",
            renderCell: (params: any) => (
                Math.round(params.value * 100) / 100
            ),
        },

        {
            field: "gesamt_soc",
            headerAlign: "left",
            align: "left",
            headerName: "Gesamt SOC % ",
            flex: 1,
            cellClassName: "name-column--cell",
            renderCell: (params: any) => (
                Math.round(params.value * 100) / 100
            ),

        },
        {
            field: "gesamt_batterie_leistung",
            headerAlign: "left",
            align: "left",
            headerName: "Gesamt Batterieleistung Watt",
            type: "number",
            flex: 1,
            cellClassName: "name-column--cell",
            renderCell: (params: any) => (
                Math.round(params.value * 100) / 100
            ),
        },
        {
            field: "gesamt_last",
            headerAlign: "left",
            align: "left",
            headerName: "Gesamt Last Watt",
            flex: 1,
            cellClassName: "name-column--cell",
            renderCell: (params: any) => (
                Math.round(params.value * 100) / 100
            ),

        },
    ];
    
    const handlePeriodChange = (event) => {
        setPvPeriod(enumPeriodMapping[event.target.value]); // Assuming you want to set pvPeriod here
    };


    const getDashboardData = (field: string, setter: Dispatch<React.SetStateAction<ExtractedFieldData[]>>, 
          loadingSetter: Dispatch<React.SetStateAction<boolean>>) => {

        const token = localStorage.getItem("accessToken");
        setLoading(true)
        axios.get(addSuffixToBackendURL(`netzbetreiber/dashboard/${haushaltID}?field=${field}&period=${pvPeriod}&start=${formatDate(dateRange.startDate)}&end=${formatDate(dateRange.endDate)}`)
        , {headers: { Authorization: `Bearer ${token}` }})
        .then((response) => {
            if(response.status === 200){
                setter(response.data)
                loadingSetter(false)
            }
        })
        .catch((error) => {
            if (error.response && error.response.status === 401 || error.response.status === 403) {
                navigate("/login") 
            }
            else if (error.response && error.response.status === 422) {
                console.log("Server Response on Error 422:", error.response.data);
            }  else if (error.response && error.response.status === 404) {
                setFailModalIsOpen(true)
                setLoading(false)
            }
            else {
                console.log(error);
            }
        }
        )

    }

    const downloadCSV = (data: SmartmeterData[]) => {
        const csvData = convertToCSV(data);
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
        saveAs(blob, 'smartmeter_data.csv');
    };


    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        setStateOtherwiseRedirect(setSmartMeterData, `netzbetreiber/dashboard/${haushaltID}?field=all&period=${pvPeriod}&start=${formatDate(dateRange.startDate)}&end=${formatDate(dateRange.endDate)}`,
            navigate, {Authorization: `Bearer ${token}`})
    }, [pvData, dateRange])

    const handleEditButton = () => {
        getDashboardData("pv", setPvData, setLoading)
        getDashboardData("soc", setSocData, setLoading1)
        getDashboardData("batterie", setBatterieData, setLoading2)
        getDashboardData("last", setLastData, setLoading3)

    }
    console.log(smartMeterData)
    return (
        <Box m="20px">
            
            <Header title="Smartmeter" subtitle="Übersicht über Smartmeter Daten für einen Haushalt"/>
            <Box component="form"  m="20px" sx={{display: "grid"}}>
            <TextField
            label="Haushalt ID eingeben"
            type="number"
            onChange={(e) => {setHaushaltID(Number(e.target.value))}}
            variant="outlined"
     
            InputLabelProps={{
                style: { color: `${colors.color1[500]}` }
            }}
            sx={{
                gridColumn: "span 4",
                '& .MuiInputBase-input': { color: `${colors.color1[500]} !important`,
                },
                '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: `${colors.color1[500]} !important`,
                },
            }}
            />
           
            <FormControl fullWidth sx={{
                gridColumn: "span 4",
                '& .MuiInputBase-input': { color: `${colors.color1[500]} !important`,
                },
                '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: `${colors.color1[500]} !important`,
                },
                '& .MuiSelect-outlined': { 
                    color: `${colors.color1[500]} !important`,
                },
                '& .MuiFormLabel-root': {
                    color: `${colors.color1[500]} !important`,
                },
                mt: "20px"
            }}>
                    <InputLabel id="period-select-label">Zeitraum</InputLabel>
                    <Select
                        labelId="period-select-label"
                        id="period-select"
                        value={reverseEnumPeriodMapping[pvPeriod]}
                        label="Zeitraum"
                        onChange={handlePeriodChange}
                    >
                        {Object.values(Period).map((p) => {
                            return <MenuItem key={p} value={p}>{p}</MenuItem>
                        })}
                    </Select>
                </FormControl>
                <Box display="flex" justifyContent="end" mt="20px" gridColumn= "span 4">
               <Button  sx={{background: theme.palette.mode == "dark" ? "black" : "white", border: `1px solid ${colors.color1[400]}`,
                width:"100%", color: colors.color1[400]}} variant="contained"
                onClick={toggleDateRangePicker}>
                Zeitraum auswählen
              </Button>
              </Box>
                <DateRangePicker
                open={openDateRangePicker}
                closeOnClickOutside={true}
                onChange={(range) => {
                    setDateRange(range);
                setOpenDateRangePicker(false);
                }}
                initialDateRange={dateRange}
            />
           <Box display="flex" justifyContent="space-evenly" mt="20px" gridColumn= "span 4">
              <Button
              onClick={() => downloadCSV(smartMeterData)}
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
              <Button  sx={{
              backgroundColor: colors.color1[400],
              color: theme.palette.background.default,
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
              ":hover" : {
                backgroundColor: colors.grey[500],
              
              },
              
            }} variant="contained"
              onClick={handleEditButton}>
                Daten zeigen
              </Button>
            </Box>
            </Box>
            {(loading && loading1 && loading2 && loading3) ? 
            (<Box display="flex" justifyContent="center" alignItems="center" height="300px">
                    <CircularProgress />
                </Box>) : 
            (<Box
                component="div"
                backgroundColor=""
                display="grid"
                gap="30px"
                gridTemplateColumns="repeat(4, minmax(0, 1fr))"
            >
                 <Box gridColumn={"span 2"} m="0px">
             <Header title="Photovoltaik Erzeugung in Watt" subtitle="" variant="h3"/>
             </Box>
             <Box gridColumn={"span 2"} m="0px">
             <Header title="% SOC" subtitle="" variant="h3"/>
             </Box>
                <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 10"}
            gridColumn={"span 2"} 
            display="flex"
            alignItems="center"
           
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <LineChart isDashboard={false} data={[{id:"gesamt_pv_erzeugung", data: periodMapping[pvPeriod](pvData)}]} 
                tickInterval={intervalMapping[pvPeriod]} enablePoints={false} marginRight={10} legendOffset={-60} ylabel="Watt PV Erzeugung"/>
                 </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 10"}
            gridColumn={"span 2"} 
            display="flex"
            alignItems="center"
            
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <LineChart isDashboard={false} data={[{id:"gesamt_soc", data: periodMapping[pvPeriod](socData)}]} 
                tickInterval={intervalMapping[pvPeriod]} enablePoints={false} marginRight={10} legendOffset={-60} ylabel="% SOC"/>
                 </Box>
            </Grow>
            <Box gridColumn={"span 2"} m="0px">
             <Header title="Batterieleistung in Watt" subtitle="" variant="h3"/>
             </Box>
             <Box gridColumn={"span 2"} m="0px">
             <Header title="Gesamtlast in Watt" subtitle="" variant="h3"/>
             </Box>
        <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 12"}
            gridColumn={"span 2"} 
            display="flex"
            alignItems="center"
          
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <LineChart isDashboard={false} data={[{id:"gesamt_pv_erzeugung", data: periodMapping[pvPeriod](batterieData)}]} 
                tickInterval={intervalMapping[pvPeriod]} enablePoints={false} marginRight={10} legendOffset={-60} ylabel="Watt Batterieleistung"/>
                 </Box>
        </Grow>
        <Grow in={true} timeout={1000}>
            <Box 
            gridRow={"span 12"}
            gridColumn={"span 2"} 
            display="flex"
            alignItems="center"
            
          
            borderRadius={"15px"}
            boxShadow="0px 6px 6px rgba(0, 0, 0, 0.4)"
            justifyContent="center">
               
                <LineChart isDashboard={false} data={[{id:"gesamt_pv_erzeugung", data: periodMapping[pvPeriod](lastData)}]} 
                tickInterval={intervalMapping[pvPeriod]} enablePoints={false} marginRight={10} legendOffset={-60} ylabel="Watt Gesamtlast"/>
                 </Box>
        </Grow>

            
                </Box>)}

            <Box
                m="20px 0 0 0"
                gridColumn={"span-4"}
                sx={{
                    "& .MuiDataGrid-cell": {
                        color: colors.grey[400],
                        borderBottom: "none",
                    },
                    "& .name-column--cell": {
                        color: colors.grey[400]
                    },
                    "& .MuiDataGrid-columnHeaders": {
                        backgroundColor: "",
                        color: colors.grey[400],
                        borderBottom: "none",
                    }
                }}

            >
                {console.log(smartMeterData)}
                <DataGrid  getRowId={(row) => row.datum} rows={smartMeterData}
                           columns={columns} hideFooter={false}/>
            </Box>


            <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
             text="Keine Daten für diesen Haushalt für diese Zeitangabe gefunden" />
        </Box>
    )
}

export default NetzbetreiberSmartmeterOverview;