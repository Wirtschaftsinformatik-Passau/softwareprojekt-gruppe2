import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import {Button} from "@mui/material";
import {useNavigate} from "react-router-dom";
import listPlugin from "@fullcalendar/list";
import { useEffect, useState } from "react";
import axios from "axios";
import {
  Box,
  List,
  ListItem,
  ListItemText,
  Typography,
  useTheme,
} from "@mui/material";
import Header from "../../utility/Header";
import { tokens } from "../../../utils/theme";
import { setStateOtherwiseRedirect } from "../../../utils/stateUtils";
import SuccessModal from "../../utility/SuccessModal";
import { addSuffixToBackendURL } from "../../../utils/networking_utils";


const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("de-at", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
};
interface DateEvent {
  title: string,
  start: string,
  end: string,
  allDay: boolean,
}

interface RequestPayLoad {
  beschreibung: string,
  start: string,
  ende: string,
  allDay: boolean,
}

const Calendar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();
  const [currentEvents, setCurrentEvents] = useState<DateEvent[] | null>([]);
  const [successModalIsOpen, setSuccessModalIsOpen] = useState<boolean>(false);
  const [failModalIsOpen, setFailModalIsOpen] = useState<boolean>(false);
  const [currentDate, setCurrentDate] = useState(null);
  const [initialEvents, setInitialEvents] = useState<DateEvent[] | null>(null);
  const [changeTracker, setChangeTracker] = useState<boolean>(false);


  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get(addSuffixToBackendURL("admin/kalendereintrag"), {
      headers: { Authorization: `Bearer ${token}` }
    }).then(response => {
      const mappedEvents = response.data.map(event => ({
        title: event.beschreibung,
        start: event.start,
        end: event.ende,
        allDay: event.allDay
      }));
      setInitialEvents(mappedEvents);

    }).catch(/* handle errors */);
  }, [changeTracker]);


  const addEvent = () => {
    if (currentDate === null) {
      return;
    }
    console.log(currentDate)
    const title = prompt("Please enter a new title for your event");
    const calendarApi = currentDate.view.calendar;
    calendarApi.unselect();

    if (title) {
      const newEvent: RequestPayLoad = {
        beschreibung: title,
        start: currentDate.startStr,
        ende: currentDate.endStr,
        allDay: currentDate.allDay,
    };

    const token = localStorage.getItem("accessToken");
    axios.post(addSuffixToBackendURL("admin/kalendereintrag"), newEvent, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    }).then((response) => {
        setSuccessModalIsOpen(true);
        setChangeTracker(!changeTracker);
    }).catch((error) => {
        setFailModalIsOpen(true);
    })
    }
  }

  const handleDateClick = (selected) => {
    console.log(initialEvents)
    setCurrentDate(selected);
  }  

  const handleEventClick = (selected) => {

    if (
      window.confirm(
        `Are you sure you want to delete the event '${selected.event.title}'`
      )
    ) {
      selected.event.remove();
    }
  };

  return (
    <Box m="20px">
      <Header title="Kalender" subtitle="Kalendarübersicht über aufkommende Events"/>
      <Box display={"flex"} justifyContent={"space-evenly"} mb={"15px"}>
                <Button variant="contained" color="primary" onClick={() => {addEvent()}}
                sx = {{
                    backgroundColor: `${colors.color1[500]} !important`,
                    color: theme.palette.background.default
                }}>
                    Eintrag erstellen    
                </Button>

            </Box>
      <Box display="flex" justifyContent="space-between">
        <Box
          flex="1 1 15%"
          backgroundColor={colors.color1[400]}
          p="15px"
          borderRadius="4px"
        >
          <Typography variant="h5">Events</Typography>
          <List>
            {currentEvents.map((event) => (
              <ListItem
                key={event.id}
                sx={{
                  backgroundColor: colors.color1[300],
                  margin: "10px 0",
                  borderRadius: "2px",
                }}
              >
                <ListItemText
                  primary={event.title}
                  secondary={
                    <Typography>
                      {formatDate(event.start, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
        <Box flex="1 1 100%" ml="15px" backgroundColor={theme.palette.background.default}

        sx={
          {
            color: colors.color1[400],
            "& .fc-button":{
              backgroundColor: colors.color1[400],
            },
            "& .fc-button-primary":{
              backgroundColor: colors.color1[400],
              border: null, 
              borderColor: colors.color1[400],
              color: theme.palette.background.default
            },
            ".fc .fc-button-primary:not(:disabled).fc-button-active, .fc .fc-button-primary:not(:disabled):active": {
              backgroundColor: colors.color1[600],
              borderColor: colors.color1[600],
              
            }
          }
        }>
          <FullCalendar
  
            height="75vh"
            plugins={[
              dayGridPlugin,
              timeGridPlugin,
              interactionPlugin,
              listPlugin,
            ]}
            headerToolbar={{
              left: "prev,next today",
              center: "title",
              right: "dayGridMonth,timeGridWeek,timeGridDay,listMonth",
            }}
            initialView="dayGridMonth"
            editable={true}
            selectable={true}
            selectMirror={true}
            dayMaxEvents={true}
            select={handleDateClick}
            eventClick={handleEventClick}
            eventsSet={(events) => setCurrentEvents(events)}
            events={initialEvents }
          />
        </Box>
      </Box>
      <SuccessModal open={successModalIsOpen} handleClose={() => setSuccessModalIsOpen(false)} 
    text="Eintrag erfolgreich erstellt!"/>
    <SuccessModal open={failModalIsOpen} handleClose={() => setFailModalIsOpen(false)} 
    text="Eintrag konnte nicht erstellt werden!"/>
    </Box>
  );
};

export default Calendar;