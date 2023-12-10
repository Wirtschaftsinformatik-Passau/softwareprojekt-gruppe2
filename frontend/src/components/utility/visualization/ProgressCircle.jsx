import { Box, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";

const ProgressCircle = ({ progress = "0.75", size = "40" }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const angle = progress * 360;
  return (
    <Box
      sx={{
        background: `radial-gradient(${colors.color1[400]} 55%, transparent 56%),
            conic-gradient(transparent 0deg ${angle}deg, ${colors.grey[300]} ${angle}deg 360deg),
            ${theme.palette.background.default}`,
        borderRadius: "50%",
        width: `${size}px`,
        height: `${size}px`,
      }}
    />
  );
};

export default ProgressCircle;