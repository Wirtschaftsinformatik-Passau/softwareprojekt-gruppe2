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

  const CustomTooltip = ({ point }) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    
    console.log(point)
    return (
      <div style={{ color: colors.color1[400] }}>
        <div><strong>ID:</strong> {point.serieId}</div>
        <div><strong>Date:</strong> {point.data.xFormatted}</div>
        <div><strong>Value:</strong> {point.data.yFormatted}</div>
      </div>
    );
  };

  return (
      <ResponsiveLine
      sliceTooltip={({ slice }) => {
        return (
            <div
                style={{
                    background: 'white',
                    padding: '9px 12px',
                    border: '1px solid #ccc',
                }}
            >
                <div>x: {slice.id}</div>
                {slice.points.map(point => (
                    <div
                        key={point.id}
                        style={{
                            color: point.serieColor,
                            padding: '3px 0',
                        }}
                    >
                        <strong>{point.serieId}</strong> [{point.data.yFormatted}]
                    </div>
                ))}
            </div>
        )
    }}
      colors={{ scheme: 'set3' }}
          data={data}
          margin={{ top: 50, right: 180, bottom: 50, left: 60 }}
          xScale={{ type: 'point' }}
          yScale={{
              type: 'linear',
              min: 'auto',
              max: 'auto',
              stacked: false,
              reverse: false
          }}
          yFormat=" >-.2f"
          axisTop={null}
          axisRight={null}
          axisBottom={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: 'Datum',
              legendOffset: 36,
              legendPosition: 'middle',
              
          }}
          axisLeft={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: 'count',
              legendOffset: -40,
              legendPosition: 'middle'
          }}
          pointSize={10}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabelYOffset={-12}
          useMesh={true}
         
          legends={[
              {
                  anchor: 'bottom-right',
                  direction: 'column',
                  justify: false,
                  translateX: 100,
                  translateY: 0,
                  itemsSpacing: 0,
                  itemDirection: 'left-to-right',
                  itemWidth: 80,
                  itemHeight: 20,
                  itemOpacity: 0.75,
                  symbolSize: 12,
                  symbolShape: 'circle',
                  symbolBorderColor: 'rgba(0, 0, 0, .5)',
                  effects: [
                      {
                          on: 'hover',
                          style: {
                              itemBackground: 'rgba(0, 0, 0, .03)',
                              itemOpacity: 1
                          }
                      }
                  ]
              }
          ]}
      />
  );
};

export default LineChart;
