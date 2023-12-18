import { useTheme } from "@mui/material";
import { ResponsiveBar } from "@nivo/bar";
import { tokens } from "../../../utils/theme";

const mockBarData = [
    {
      "date": "03.12.2023",
      "value": 10
    },
    {
      "date": "04.12.2023",
      "value": 1
    },
    {
      "date": "06.12.2023",
      "value": 1
    },
    {
      "date": "11.12.2023",
      "value": 13
    },
    {
      "date": "12.12.2023",
      "value": 7
    },
    {
      "date": "14.12.2023",
      "value": 4
    },
    {
      "date": "16.12.2023",
      "value": 9
    },
    {
      "date": "18.12.2023",
      "value": 6
    },
    {
      "date": "20.12.2023",
      "value": 3
    },
    {
      "date": "22.12.2023",
      "value": 11
    }
]


const BarChart = ({ data= mockBarData, isDashboard = false, key="date", legend="Datum", indexBy="date", ylabel="Anzahl Aufrufe"}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <ResponsiveBar
     data={data}
      keys={['value']}
      indexBy={indexBy}  
      theme={{
        axis: {
          domain: {
            line: {
              stroke: colors.grey[100],
            },
          },
          legend: {
            text: {
              fill: colors.grey[300],
            },
          },
          ticks: {
            line: {
              stroke: colors.grey[300],
              strokeWidth: 1,
            },
            text: {
              fill: colors.grey[300],
            },
          },
        },
        legends: {
          text: {
            fill: colors.grey[300],
          },
        },
    }}
    tooltip={({ value, indexValue }) => {
      return <div style={{padding: "10px", backgroundColor: theme.palette.background.default, color: colors.grey[100], borderRadius: "4px"}}>
        {indexValue}: {value}</div>
          }}
          
      margin={{ top: 50, right: 10, bottom: 50, left: 60 }}
      padding={0.3}
      valueScale={{ type: "linear" }}
      indexScale={{ type: "band", round: true }}
      colors={colors.color1[400]}
        colorBy="index"
      defs={[
        {
          id: "dots",
          type: "patternDots",
          background: "inherit",
          color: "#38bcb2",
          size: 4,
          padding: 1,
          stagger: true,
        },
        {
          id: "lines",
          type: "patternLines",
          background: colors.color1[500],
          color: colors.color1[500],
          rotation: -45,
          lineWidth: 6,
          spacing: 10,
        },
      ]}
      borderColor={{
        from: "color",
        modifiers: [["darker", "1.6"]],
      }}
      axisTop={null}
      axisRight={null}
      axisBottom={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: legend,
        legendPosition: "middle",
        legendOffset: isDashboard ? 10 : 32,
        tickValues: isDashboard ? undefined :  data.map((item, index) => index % 3 === 0 ? item[indexBy] : null).filter(Boolean), // Updated line
    }}
      axisLeft={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: isDashboard ? undefined : ylabel, // changed
        legendPosition: "middle",
        legendOffset: -40,
      }}
      enableLabel={false}
      labelSkipWidth={12}
      labelSkipHeight={12}
      labelTextColor={{
        from: "color",
        modifiers: [["darker", 1.6]],
      }}
      animate={true}
      legends={[]}
      role="application"
      
    />
  );
};

export default BarChart;