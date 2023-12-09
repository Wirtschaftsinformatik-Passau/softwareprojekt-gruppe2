import { Typography, Box, useTheme } from "@mui/material";
import { tokens } from "../../utils/theme";
import React from "react";



interface HeaderProps {
    title: string;
    subtitle: string;
    textAlign?: "left" | "center" | "right";
    
}

const Header: React.FC<HeaderProps> = ({title, subtitle, textAlign="center"}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <Box mb="30px" textAlign={textAlign}>
      <Typography
        variant="h2"
        color={colors.color1[500]}
        fontWeight="bold"
        sx={{ m: "0 0 8px 0" }}
      >
        {title}
      </Typography>
      <Typography variant="h5" color={colors.color2[400]}   borderBottom={`2px solid ${colors.color2[100]}`}>
        {subtitle}
      </Typography>
    </Box>
  );
};

export default Header;