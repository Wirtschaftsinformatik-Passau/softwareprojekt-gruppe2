import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";


const mockData =[
  {
      "id": "login",
      "data": [
          { "x": "05.12.2023", "y": 20 },  // Angenommener Zufallswert
          { "x": "06.12.2023", "y": 45 },
          { "x": "07.12.2023", "y": 50 },  // Angenommener Zufallswert
          { "x": "08.12.2023", "y": 30 },  // Angenommener Zufallswert
          { "x": "09.12.2023", "y": 85 },  // Angenommener Zufallswert
          { "x": "10.12.2023", "y": 60 },  // Angenommener Zufallswert
          { "x": "11.12.2023", "y": 75 }   // Angenommener Zufallswert
      ]
  },
  {
      "id": "registration",
      "data": [
          { "x": "05.12.2023", "y": 40 },  // Angenommener Zufallswert
          { "x": "06.12.2023", "y": 55 },  // Angenommener Zufallswert
          { "x": "07.12.2023", "y": 65 },  // Angenommener Zufallswert
          { "x": "08.12.2023", "y": 35 },  // Angenommener Zufallswert
          { "x": "09.12.2023", "y": 95 },  // Angenommener Zufallswert
          { "x": "10.12.2023", "y": 80 },  // Angenommener Zufallswert
          { "x": "11.12.2023", "y": 70 }   // Angenommener Zufallswert
      ]
  },
  {
      "id": "dashboard",
      "data": [
          { "x": "05.12.2023", "y": 30 },  // Angenommener Zufallswert
          { "x": "06.12.2023", "y": 45 },  // Angenommener Zufallswert
          { "x": "07.12.2023", "y": 55 },  // Angenommener Zufallswert
          { "x": "08.12.2023", "y": 65 },  // Angenommener Zufallswert
          { "x": "09.12.2023", "y": 75 },  // Angenommener Zufallswert
          { "x": "10.12.2023", "y": 85 },  // Angenommener Zufallswert
          { "x": "11.12.2023", "y": 95 }   // Angenommener Zufallswert
      ]
  }
]

const mockData2 = [
  {
      "id": "/login",
      "data": [
          {
              "x": "11.12.2023",
              "y": 2
          },
          {
              "x": "12.12.2023",
              "y": 21
          },
          {
              "x": "13.12.2023",
              "y": 9
          },
          {
              "x": "14.12.2023",
              "y": 2
          }
      ]
  },
  {
      "id": "/registration",
      "data": [
          {
              "x": "12.12.2023",
              "y": 10
          },
          {
            "x": "13.12.2023",
            "y": 43
        }
        ,{
          "x": "14.12.2023",
          "y": 20
      }
      ]
  },
  {
      "id": "/userOverview",
      "data": [
          {
              "x": "13.12.2023",
              "y": 43
          },
          {
              "x": "14.12.2023",
              "y": 20
          }
      ]
  },]


const LineChart = ({ data = mockData2,isDashboard = false }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  console.log(data);

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
        stacked: false,
        reverse: false,
      }}
      yFormat=" >-.2f"
      curve="linear"
      axisTop={null}
      axisRight={null}
      axisBottom={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: "Datum",
        legendPosition: "middle",
        legendOffset: isDashboard ? 10 : 32,
        tickValues: isDashboard ? undefined :  data.map((item, index) => index % 3 === 0 ? item.date : null).filter(Boolean), // Updated line
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
