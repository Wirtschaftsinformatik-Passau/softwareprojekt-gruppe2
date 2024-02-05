import { Box, IconButton, useTheme, Typography, TextField} from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import {makeStyles} from "@material-ui/core/styles";
import { useContext, useState, useEffect } from "react";
import {ColorModeContext, tokens} from "../../utils/theme.js";
import LogoutIcon from '@mui/icons-material/Logout';
import { useNavigate } from "react-router-dom";
import InputBase from "@mui/material/InputBase";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import SearchIcon from "@mui/icons-material/Search";
import useMediaQuery from "@mui/material/useMediaQuery/useMediaQuery";
import {searchBarItems} from "../../entitities/utils";
import HelpModal from "../utility/HelpModal";
import { navigateToHome } from "../../utils/navigateUtils.js";

import logo from "../../assets/logo_large.png"

const useStyles = makeStyles((theme) => ({
    paper: {
        border: '1px solid #ddd',
        backgroundColor: theme.palette.background.default,
        color: "#386641",
        borderRadius: 4,
        boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2)',
        // Add other styling as needed
    },
    option: {
        '&:hover': {
            backgroundColor: "#707274", // Styling for hover stater state
        },

    }
}));

const Topbar = ({fixed, nutzerrolle, search=true}) => {
    const navigate = useNavigate();
    const isNonMobile = useMediaQuery("(min-width:700px)")
    const [helpModal, setHelpModal] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [inputValue, setInputValue] = useState("");
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const classes = useStyles(theme);
    const colorMode = useContext(ColorModeContext);


    const handleSearchItemSelected = (event, item) => {
        if (item) navigate(item.link);
    };

    const handleInputChange = (event, newInputValue) => {
        setInputValue(newInputValue);
    };

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
                <Box onClick={() => navigateToHome(nutzerrolle, navigate)}
                sx={{cursor:"pointer"}}>
                    <img src={logo} alt="GreenEcoHub Logo" style={{width: "250px", height: "50px"}}/>
                   
                </Box>
                <Box
                    display="flex"
                    backgroundColor={theme.palette.background.default}

                    borderRadius="3px"
                    sx={{
                        '& .MuiInputBase-input': {
                            color: `${colors.color1[500]} !important`,
                        },

                        "& .MuiInputLabel-root": {
                            color: `${colors.color1[500]} !important`,
                        },

                        }
                    }

                >
                    {search && (
                        <Autocomplete
                            freeSolo
                            onChange={handleSearchItemSelected}
                            inputValue={inputValue}
                            onInputChange={handleInputChange}
                            options={searchBarItems[nutzerrolle]}
                            classes={{
                                paper: classes.paper, // Apply your custom styles to the dropdown
                                option: classes.option, // Apply custom styles to each option
                            }}
                            getOptionLabel={(option) => option.label}
                            renderInput={(params) => <TextField {...params} label={<SearchIcon />} />}
                            sx={{ width: 200 }}
                        />

                        )}

                </Box>
            </Box>


           <Box display="flex">
           {search && (
                <IconButton onClick={colorMode.toggleColorMode}>
                    {theme.palette.mode === "dark" ? (
                        <DarkModeOutlinedIcon />
                    ) : (
                        <LightModeOutlinedIcon />
                    )}
        
                </IconButton>
           )}
                <IconButton onClick={() => setHelpModal(true)}>
                    <QuestionMarkIcon />
                </IconButton>
                {search && (
                    <IconButton>
                    <PersonOutlinedIcon onClick={() => navigate("/profile")}/>
                </IconButton>
                )
}
                <IconButton>
                    <LogoutIcon onClick={() => {
                        navigate("/login")

                    }}/>
                </IconButton>
            </Box>
            {helpModal && (<HelpModal modalCloserState={setHelpModal} nutzerrolle={nutzerrolle} navigateFN={navigate}/>)}
        </Box>
    );
};

export default Topbar;