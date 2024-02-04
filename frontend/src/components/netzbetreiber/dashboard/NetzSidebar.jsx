import { useState, useEffect } from "react";
import { useLocation, useNavigate, useParams, Link } from "react-router-dom";
import { ProSidebar, Menu, MenuItem } from "react-pro-sidebar";
import { Box, IconButton, Typography, useTheme } from "@mui/material";
import axios from "axios";
import "react-pro-sidebar/dist/css/styles.css";
import { tokens } from "../../../utils/theme";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import TableViewIcon from '@mui/icons-material/TableView';
import PeopleOutlinedIcon from "@mui/icons-material/PeopleOutlined";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import HolidayVillageIcon from '@mui/icons-material/HolidayVillage';
import DashboardIcon from '@mui/icons-material/Dashboard';import PieChartOutlineOutlinedIcon from "@mui/icons-material/PieChartOutlineOutlined";
import ClearIcon from '@mui/icons-material/Clear';
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import AddBoxIcon from '@mui/icons-material/AddBox';
import ReceiptIcon from '@mui/icons-material/Receipt';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import EditIcon from '@mui/icons-material/Edit';
import ChatBubbleIcon from '@mui/icons-material/ChatBubble';
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import {addSuffixToBackendURL} from "../../../utils/networking_utils.js";

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
      <Link to={"/netzbetreiber" + to} />
    </MenuItem>
  );
};

const NetzbetreiberSidebar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selected, setSelected] = useState("");
  const location = useLocation();
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  const [isArbeitgeber, setIsArbeitgeber] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setStateOtherwiseRedirect(setCurrentUser, "users/current/single", navigate,  {Authorization: `Bearer ${token}`})
    console.log(currentUser)
  }, [])

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get(addSuffixToBackendURL("netzbetreiber/check-arbeitgeber"),
        {headers: {Authorization: `Bearer ${token}`}})
        .then((res) => {
          setIsArbeitgeber(res.data.is_arbeitgeber)
        })
        .catch((err) => {
          console.log(err.response.data)
        })
  }, [])



  return (
    <Box
    sx={{
      "minHeight": "100vh",
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
              selected={location.pathname === "/admin" ? "Dashboard" : selected}
              setSelected={setSelected}
          
            />

            {isArbeitgeber && (
                <>
                <Typography
                    variant="h6"
                    color={colors.white[200]}
                    sx={{ m: "15px 0 5px 20px" }}
                >
                  Mitarbeiter
                </Typography>
              <Item
              title="Mitarbeiterübersicht"
              to="/mitarbeiterTable"
              icon={<PeopleOutlinedIcon/>}
            selected={selected}
            setSelected={setSelected}
          />
          <Item
              title="Mitarbeiter erstellen"
              to="/mitarbeiterCreate"
              icon={<PersonAddIcon />}
              selected={selected}
              setSelected={setSelected}
          />
                </>
                )}

            <Typography
              variant="h6"
              color={colors.white[200]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Tarife
            </Typography>
            <Item
              title="Tarifübersicht"
              to="/tarifTable"
              icon={<TableViewIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Tarif erstellen"
              to="/tarifCreate"
              icon={<AddBoxIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Tarif bearbeiten"
              to="/tarifEdit"
              icon={<EditIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Laufende Verträge"
              to="/vertraege"
              icon={<ReceiptIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Kündigungsanfragen"
              to="/vertraegeKuendigung"
              icon={<ClearIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
             <Typography
              variant="h6"
              color={colors.white[200]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Preise
            </Typography>
            <Item
              title="Preisübersicht"
              to="/priceTable"
              icon={<AttachMoneyIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Preis erstellen"
              to="/priceCreate"
              icon={<AddBoxIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Preis bearbeiten"
              to="/priceEdit"
              icon={<EditIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
          <Typography
              variant="h6"
              color={colors.white[300]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Board
            </Typography>
            <Item
              title="Smart Meter Upload"
              to="/smartmeterUpload"
              icon={<FileUploadIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Smart Meter Übersicht"
              to="/smartmeterOverview"
              icon={<DashboardIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Typography
              variant="h6"
              color={colors.white[300]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              PV
            </Typography>
            <Item
              title="Übersicht Haushalte"
              to="/haushalteOverview"
              icon={<HolidayVillageIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Offene Anträge"
              to="/einspeisungen"
              icon={<AccessTimeIcon />}
              selected={selected}
              setSelected={setSelected}
            />
            <Item
              title="Angenommene Anträge"
              to="/einspeisungenAngenommen"
              icon={< CheckBoxIcon/>}
              selected={selected}
              setSelected={setSelected}
            />
            <Typography
              variant="h6"
              color={colors.white[300]}
              sx={{ m: "15px 0 5px 20px" }}
            >
              Pages
              
            </Typography>
            <Item
            title="Rechnungen"
            to="/rechnungenOverview"
            icon={<AttachMoneyIcon/>}
            selected={selected}
            setSelected={setSelected}
            />
            <Item
              title="Kalender"
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

export default NetzbetreiberSidebar;