import { useState, useEffect } from "react";
import { useLocation, useNavigate, useParams, Link } from "react-router-dom";
import { ProSidebar, Menu, MenuItem } from "react-pro-sidebar";
import { Box, IconButton, Typography, useTheme } from "@mui/material";
import "react-pro-sidebar/dist/css/styles.css";
import { tokens } from "../../../utils/theme";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import ChatBubbleIcon from '@mui/icons-material/ChatBubble';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";

import user from "../../../assets/admin_icon.png"



const Item = ({ title, to, icon, selected, setSelected }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);


  return (
    <MenuItem
      active={selected === title}
      style={{
        color: colors.white[100],
      }}
      onClick={() => setSelected(title)}
      icon={icon}
    >
      <Typography>{title}</Typography>
      <Link to={"/solarteure" + to} />
    </MenuItem>
  );
};

const SolarteureSidebar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selected, setSelected] = useState("");
  const location = useLocation();
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setCurrentUser, "users/current/single", navigate,  {Authorization: `Bearer ${token}`})
    console.log(currentUser)
  }, [])



  return (
    <Box
    sx={{
      "minHeight": "100vh",
      "& .pro-sidebar": {
        width: isCollapsed ? "90px !important" : "280px !important",
      },
      "& .pro-sidebar-inner": {
        background: `${colors.color1[400]} !important`,
        width: isCollapsed ? "90% !important" : "100% !important",
      },
      "& .pro-icon-wrapper": {
        backgroundColor: "transparent !important",
      },
      "& .pro-inner-item:hover": {
        color: `${colors.color1[500]} !important`,
        backgroundColor: `white !important`,
      },
      "& .pro-menu-item.active": {
          color: `${colors.color5[600]} !important`,
      },
      "& .pro-inner-item.pro-inner-item": {
        padding: "5px 35px 5px 20px !important",
      },
      "&::-webkit-scrollbar": {
        display: "none"
      },

    }}
    style={{
      overflow: "auto",
      scrollbarWidth: "none", 
      msOverflowStyle: "none",
      color: theme.palette.background.default,
    }}
    >
      <ProSidebar collapsed={isCollapsed}>
        <Menu iconShape="square">
          <MenuItem
            onClick={() => setIsCollapsed(!isCollapsed)}
            icon={isCollapsed ? <MenuOutlinedIcon /> : undefined}
            style={{
              margin: "10px 0 20px 0",
              color: theme.palette.backgroundColor,
            }}
          >
            {!isCollapsed && (
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                ml="1px"
              >
                <IconButton onClick={() => setIsCollapsed(!isCollapsed)}>
                  <MenuOutlinedIcon />
                </IconButton>
              </Box>
            )}
          </MenuItem>

          {!isCollapsed && (
            <Box mb="25px">
              <Box display="flex" justifyContent="center" alignItems="center">
                <img
                  alt="profile-user"
                  width="100px"
                  height="100px"
                  backgroundColor="transparent"
                  src={user}
                  style={{ cursor: "pointer", borderRadius: "50%" }}
                />
              </Box>
              <Box textAlign="center">
                <Typography
                  variant="h2"
                  color={theme.palette.background.default}
                  fontWeight="bold"
                  sx={{ m: "10px 0 0 0" }}
                >
                  {currentUser && currentUser.vorname} {currentUser && currentUser.nachname}
                </Typography>
                <Typography variant="h5" color={colors.grey[300]}>
                  {currentUser && currentUser.email}
                </Typography>
              </Box>
            </Box>
          )}

          <Box paddingLeft={isCollapsed ? undefined : "8%"}>
            <Item
              title="Dashboard"
              to="/"
              icon={<HomeOutlinedIcon />}
              selected={location.pathname === "/solarteure" ? "Dashboard" : selected}
              setSelected={setSelected}
          
            />

            <Typography
              variant="h6"
              color={colors.white[200]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Anträge
            </Typography>
            <Item
              title="Offene Anträge"
              to="/antragTable"
              icon={<TrackChangesIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Bearbeitete Anträge"
              to="/antragTableBearbeitet"
              icon={<AccessTimeIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
             <Item
              title="Abgeschlossene Anträge"
              to="/antragTableAbgeschlossen"
              icon={<CheckBoxIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
             <Item
            title="Rechnungen"
            to="/rechnungenOverview"
            icon={<AttachMoneyIcon/>}
            selected={selected}
            setSelected={setSelected}
            />
             <Typography
              variant="h6"
              color={colors.white[200]}
              sx={{ m: "15px 0 5px 20px" }}
            >
             
              Pages
            </Typography>
            <Item
              title="Calendar"
              to="/calendar"
              icon={<CalendarTodayOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Chat"
              to="/chat"
              icon={<ChatBubbleIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="FAQ Page"
              to="/faq"
              icon={<HelpOutlineOutlinedIcon />}
              selected={selected}
              setSelected={setSelected}
            />

            
          </Box>
        </Menu>
      </ProSidebar>
    </Box>
  );
};

export default SolarteureSidebar;