import { Box, IconButton, useTheme, Typography } from "@mui/material";
import { useContext, useState } from "react";
import { ColorModeContext, tokens } from "../../../utils/theme";
import LogoutIcon from '@mui/icons-material/Logout';
import { useNavigate } from "react-router-dom";
import InputBase from "@mui/material/InputBase";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import SearchIcon from "@mui/icons-material/Search";
import HelpModal from "../../utility/HelpModal";
import useMediaQuery from "@mui/material/useMediaQuery/useMediaQuery";
import { Link } from "react-router-dom";

import logo from "../../../assets/logo_large.svg"


const Topbar = ({fixed, search=true}) => {
  const navigate = useNavigate();
    const isNonMobile = useMediaQuery("(min-width:700px)")
    const [helpModal, setHelpModal] = useState(false);
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const colorMode = useContext(ColorModeContext);
  
    return (
      <Box display="flex" justifyContent="space-between" p={2} 
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
            color: theme.palette.neutral.background,
            fontWeight: "bold",
          }}>
            GreenEcoHub
          </Typography>
        </Box>
        <Box
          display="flex"
          backgroundColor={theme.palette.background.default}

          borderRadius="3px"
        >
          {search &&(
            <>
          <InputBase sx={{ ml: 2, flex: 1, color: theme.palette.neutral.main}} placeholder="Search" />
          <IconButton type="button" sx={{ p: 1, color: theme.palette.neutral.main}} >
            <SearchIcon />
          </IconButton>
          </>
          )
}
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
            <PersonOutlinedIcon onClick={() => navigate("/profile")}/>
          </IconButton>
          <IconButton>
            <LogoutIcon onClick={() => {
              navigate("/login")
   
            }}/>
          </IconButton>
        </Box>
        {helpModal && (<HelpModal modalCloserState={setHelpModal}/>)}
      </Box>
    );
  };
  
  export default Topbar;