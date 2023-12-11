import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../utils/theme";
import ProgressCircle from "./ProgressCircle";

const StatBox = ({ title, subtitle, icon, progress, increase }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box width="100%" m="0 0px" sx={
      {background: colors.color1[400], ":hover": {background: colors.color1[500], cursor: "pointer"}}
      } p="10px" borderRadius={"15px"} boxShadow="0px 8px 8px rgba(0, 0, 0, 0.4)">
      <Box display="flex" justifyContent="space-between">
        <Box sx={{ color: theme.palette.background.default }}s>
          {icon}
          <Typography
            variant="h4"
            fontWeight="bold"
            sx={{ color: theme.palette.background.default }}
          >
            {title}
          </Typography>
        </Box>
        <Box>
          <ProgressCircle progress={progress} />
        </Box>
      </Box>
      <Box display="flex" justifyContent="space-between" mt="4px">
        <Typography variant="h5" sx={{ color: theme.palette.background.default }}>
          {subtitle}
        </Typography>
        <Typography
          variant="h5"
          fontStyle="italic"
          sx={{ color: theme.palette.background.default }}
        >
          {increase}
        </Typography>
      </Box>
    </Box>
  );
};

export default StatBox;