import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";


const mockData =[
    {"id": "login",
    "data": [
        { x: "05.12.2023", y: Math.random() * 100 },
            { x: "06.12.2023", y: 45 },
            { x: "07.12.2023", y: Math.random() * 100 },
            { x: "08.12.2023", y: Math.random() * 100 },
            { x: "09.12.2023", y: Math.random() * 100 }
    ]},
    {
        "id": "registration",
        "data": [
            { x: "05.12.2023", y: Math.random() * 100 },
            { x: "06.12.2023", y: Math.random() * 100 },
            { x: "07.12.2023", y: Math.random() * 100 },
            { x: "08.12.2023", y: Math.random() * 100 },
            { x: "09.12.2023", y: Math.random() * 100 }
        ]
    },
    {
        "id": "dashboard",
        "data": [
            { x: "05.12.2023", y: Math.random() * 100 },
            { x: "06.12.2023", y: Math.random() * 100 },
            { x: "07.12.2023", y: Math.random() * 100 },
            { x: "08.12.2023", y: Math.random() * 100 },
            { x: "09.12.2023", y: Math.random() * 100 }
        ]
    }
]

const LineChart = ({ data = mockData,isDashboard = false }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const colorScheme = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"];

  const getColor = (bar) => colorScheme[bar.index%10];

  return (
    <ResponsiveLine
      data={data}
      theme={{
        axis: {
          domain: {
            line: {
              stroke: colors.grey[100],
            },
          },
          legend: {
            text: {
              fill: colors.grey[100],
            },
          },
          ticks: {
            line: {
              stroke: colors.grey[100],
              strokeWidth: 1,
            },
            text: {
              fill: colors.grey[100],
            },
          },
        },
        legends: {
          text: {
            fill: colors.grey[100],
          },
        },
        tooltip: {
          container: {
            color: colors.color1[500],
          },
        },
      }}
      colors={[colors.color1[500], colors.color3[500], colors.color5[500]]}
      margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
      xScale={{ type: "point" }}
      yScale={{
        type: "linear",
        min: "auto",
        max: "auto",
        stacked: true,
        reverse: false,
      }}
      yFormat=" >-.2f"
      curve="linear"
      axisTop={null}
      axisRight={null}
      axisBottom={{
        orient: "bottom",
        tickSize: 0,
        tickPadding: 5,
        tickRotation: 0,
        legend: isDashboard ? undefined : "Datum", // added
        legendOffset: 36,
        legendPosition: "middle",
      }}
      axisLeft={{
        orient: "left",
        tickValues: 5, // added
        tickSize: 3,
        tickPadding: 5,
        tickRotation: 0,
        legend: isDashboard ? undefined : "Anzahl Aufrufe im Backend", // added
        legendOffset: -40,
        legendPosition: "middle",
      }}
      enableGridX={true}
      enableGridY={true}
      pointSize={8}
      pointColor={{ theme: "background" }}
      pointBorderWidth={2}
      pointBorderColor={{ from: "serieColor" }}
      pointLabelYOffset={-12}
      useMesh={true}
      legends={[
        {
          anchor: "bottom-right",
          direction: "column",
          justify: false,
          translateX: 100,
          textColor: 'white',
          translateY: 0,
          itemsSpacing: 0,
          itemDirection: "left-to-right",
          itemWidth: 80,
          itemHeight: 20,
          itemOpacity: 0.75,
          symbolSize: 12,
          symbolShape: "circle",
          symbolBorderColor: "rgba(0, 0, 0, .5)",
          effects: [
            {
              on: "hover",
              style: {
                itemBackground: "rgba(0, 0, 0, .03)",
                itemOpacity: 1,
              },
            },
          ],
        },
      ]}
    />
  );
};

export default LineChart;
