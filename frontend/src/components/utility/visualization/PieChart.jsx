import { ResponsivePie } from "@nivo/pie";
import { tokens } from "../../../utils/theme";
import { useTheme } from "@mui/material";

const mockPieData = [
    {id: "Admin",
    label: "Admin",
    value: 10,},
    {id: "Nutzer",
    label: "Nutzer",
    value: 40,},
    {id: "Netzbetreiber",
    label: "Netzbetreiber",
    value: 34,},
    {id: "Berater",
    label: "Berater",
    value: 16,}, 
    {id: "Solateur",
    label: "Solateur",
    value: 30,}
]

const PieChart = ({data=mockPieData, isDashboard=false}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <ResponsivePie
      data={data}
      label="value"
      colors = {[colors.color1[400],colors.color2[500],colors.color3[500],colors.color4[500],colors.color5[500]]}
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
      }}
      margin={{ top: 40, right: 0, bottom: 80, left: 0 }}
      innerRadius={0.5}
      padAngle={0.7}
      cornerRadius={3}
      activeOuterRadiusOffset={8}
      borderColor={{
        from: "color",
        modifiers: [["darker", 0.2]],
      }}
      arcLinkLabelsSkipAngle={10}
      arcLinkLabelsTextColor={colors.grey[100]}
      arcLinkLabelsThickness={2}
      arcLinkLabelsColor={{ from: "color" }}
      enableArcLabels={false}
      arcLabelsRadiusOffset={0.4}
      arcLabelsSkipAngle={7}
      arcLabelsTextColor={{
        from: "color",
        modifiers: [["darker", 2]],
      }}
      tooltip={e => {
        return <div style={{padding: "10px", backgroundColor: theme.palette.background.default, color: colors.grey[100], borderRadius: "4px"}}>
          {e.id}</div>
            
      }}

      defs={[
        {
          id: "dots",
          type: "patternDots",
          background: "inherit",
          color: "rgba(255, 255, 255, 0.3)",
          size: 4,
          padding: 1,
          stagger: true,
        },
        {
          id: "lines",
          type: "patternLines",
          background: "inherit",
          color: "rgba(255, 255, 255, 0.3)",
          rotation: -45,
          lineWidth: 6,
          spacing: 10,
        },
      ]}
      legends={isDashboard? [] : [
        {
          anchor: "bottom",
          direction: "row",
          justify: false,
          translateX: 0,
          translateY: 56,
          itemsSpacing: 20,
          itemWidth: 100,
          itemHeight: 18,
          itemTextColor: colors.grey[300],
          itemDirection: "left-to-right",
          itemOpacity: 1,
          symbolSize: 18,
          symbolShape: "circle",
          effects: [
            {
              on: "hover",
              style: {
                itemTextColor: "black",
              },
            },
          ],
        },
      ]}
    />
  );
};

export default PieChart;