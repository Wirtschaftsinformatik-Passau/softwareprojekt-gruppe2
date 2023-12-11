import { Box, IconButton, useTheme, Typography } from "@mui/material";
import { useContext, useState } from "react";
import { ColorModeContext, tokens } from "../../../utils/theme";
import {ThemeProvider, CssBaseline } from "@mui/material";
import InputBase from "@mui/material/InputBase";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import SearchIcon from "@mui/icons-material/Search";
import HelpModal from "../../utility/HelpModal";
import useMediaQuery from "@mui/material/useMediaQuery/useMediaQuery";


const Topbar = ({fixed}) => {
    const isNonMobile = useMediaQuery("(min-width:700px)")
    const [helpModal, setHelpModal] = useState(false);
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const colorMode = useContext(ColorModeContext);
  
    return (
      <Box display="flex" justifyContent="space-between" p={2} borderBottom={`2px solid ${colors.color1[200]}`}
        sx = {fixed ? {
          position: 'fixed',
          top: 0, 
          left: 0, 
          right: 0, 
          zIndex: 1100, 
          backgroundColor: colors.color1[400],        
        } :  {backgroundColor: colors.color1[400]}}
      >
        <Box display="flex" alignItems="center" gap={isNonMobile? "10%" : "2%"}>
        <Box>
          <Typography variant="h3" 
          sx={{
            color: colors.color1[200],
            fontWeight: "bold",
          }}>
            GreenEcoHub
          </Typography>
        </Box>
        <Box
          display="flex"
          backgroundColor={colors.color1[200]}
          borderRadius="3px"
        >
          <InputBase sx={{ ml: 2, flex: 1 }} placeholder="Search" />
          <IconButton type="button" sx={{ p: 1 }}>
            <SearchIcon />
          </IconButton>
        </Box>
        </Box>
  
        
        <Box display="flex">
          <IconButton onClick={colorMode.toggleColorMode}>
            {theme.palette.mode === "dark" ? (
              <DarkModeOutlinedIcon />
            ) : (
              <LightModeOutlinedIcon />
            )}
          </IconButton>
          <IconButton onClick={() => setHelpModal(true)}>
            <QuestionMarkIcon />
          </IconButton>
          <IconButton>
            <SettingsOutlinedIcon />
          </IconButton>
          <IconButton>
            <PersonOutlinedIcon />
          </IconButton>
        </Box>
        {helpModal && (<HelpModal modalCloserState={setHelpModal}/>)}
      </Box>
    );
  };
  
  export default Topbar;