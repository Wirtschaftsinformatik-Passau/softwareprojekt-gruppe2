import React from 'react';
import { useEffect } from 'react';
import { useTheme } from '@mui/material';
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Autocomplete from "@mui/material/Autocomplete";
import Grid from '@material-ui/core/Grid';
import { useNavigate } from 'react-router-dom';
import Box from '@material-ui/core/Box';
import Divider from '@material-ui/core/Divider';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Avatar from '@material-ui/core/Avatar';
import Fab from '@material-ui/core/Fab';
import PersonIcon from '@mui/icons-material/Person';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import SearchIcon from "@mui/icons-material/Search";
import { User } from '../../entitities/user';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import { setStateOtherwiseRedirect } from '../../utils/stateUtils';
import { addSuffixToBackendURL } from '../../utils/networking_utils';
import { formatTime } from '../../utils/dateUtils';
import { tokens } from '../../utils/theme';
import { reduceUsers, ExtendedUser, SearchBarUser, 
    ChatHistory, getUniqueUsers, filterSearchBarUsers,
    setAndRequestConversationHistory } from '../../utils/chatUtils';


    const useStyles = makeStyles({
        table: {
          minWidth: 650,
        },
        chatSection: {
          width: '100%',
          height: '80vh'
        },
        headBG: {
            backgroundColor: '#e0e0e0'
        },
        borderRight500: {
            borderRight: '1px solid #e0e0e0'
        },
        messageArea: {
          height: '70vh',
          overflowY: 'auto'
        }
      });

interface SideUserProps {
    user: SearchBarUser;
    current: boolean;
    activeSetter: (user: SearchBarUser) => void;
    selectedUser: SearchBarUser;
}

const SideUser: React.FC<SideUserProps> = ({user, current, selectedUser, activeSetter = null}) => {
    return(
  <ListItem button key={user.user_id}
        onClick={() =>{
            if (activeSetter)
            activeSetter(user)
        }}
        
        selected={selectedUser && selectedUser.user_id === user.user_id}
        
  >
        <ListItemIcon>
            <Avatar alt="user">
                {current ? <SentimentSatisfiedAltIcon/> : <PersonIcon/>}
            </Avatar>
        </ListItemIcon>
        <ListItemText primary={user.label}>user.label</ListItemText>
    </ListItem>
    )
}

interface MessagesProps  {
    classes: any,
    current_user: SearchBarUser,
    selectedUser: SearchBarUser,
    history: ChatHistory[],
    historySetter : (history: ChatHistory[]) => void;
}

const Messages: React.FC<MessagesProps> = ({classes, current_user, selectedUser, history, historySetter}) => {
    const theme = useTheme();
    const [message, setMessage] = React.useState('');
    const colors = tokens(theme.palette.mode);
    useEffect(() => {
        setAndRequestConversationHistory(current_user.user_id, selectedUser.user_id, historySetter)
    }, [selectedUser, message])

    const handleInputChange = (event) => {
        setMessage(event.target.value);
    };


    const handleSendClick = () => {
        const token = localStorage.getItem("accessToken");
        const body = {
            sender_id : current_user.user_id,
            empfaenger_id : selectedUser.user_id,
            nachricht_inhalt : message,
        }
       axios.post(addSuffixToBackendURL("users/chat/send"), body, {
        headers: { Authorization: `Bearer ${token}` },
       })
       .then((res) => {
              setMessage("")
         })
            .catch((err) => {
                console.log(err.response.data)
            })
    };

    return(
    <Grid item xs={9}>
                <List className={classes.messageArea}>
                    {history.map((message) => {
                        return <ListItem key={message.nachricht_id}>
                            <Grid container>
                                <Grid item xs={12}>
                                    <ListItemText align={message.sender_id === current_user.user_id ? "right" : "left"} primary={message.nachricht_inhalt}></ListItemText>
                                </Grid>
                                <Grid item xs={12}>
                                    <ListItemText align={message.sender_id === current_user.user_id ? "right" : "left"} secondary={formatTime(message.timestamp)}></ListItemText>
                                </Grid>
                            </Grid>
                        </ListItem>
                    })}
                </List>
                <Divider />
                <Grid container style={{padding: '20px'}}>
                    <Grid item xs={11}>
                        <TextField id="outlined-basic-email" 
                        label="Nachricht eingeben" fullWidth 
                        value={message}
                        onChange={handleInputChange}/>
                    </Grid>
                    <Grid xs={1} align="right">
                        <Fab color="primary" onClick={handleSendClick} aria-label="add"><SendIcon /></Fab>
                    </Grid>
                </Grid>
            </Grid>
    )
}

const Chat = () => {
  const classes = useStyles();
  const [currentUser, setCurrentUser] = React.useState<SearchBarUser | null>(null);
  const [users, setUsers] = React.useState<SearchBarUser[]>([]); 
  const [inputValue, setInputValue] = React.useState<string>("");
  const [selectedUser, setSelectedUser] = React.useState<SearchBarUser | null>(null);
  const [userHistory, setUserHistory] = React.useState<ChatHistory[]>([]);
  const [individualHistory, setIndividualHistory] = React.useState<ChatHistory[]>([]);
  const [historyUsers, setHistoryUsers] = React.useState<SearchBarUser[]>([]);
  const navigate = useNavigate();

  const handleSearchItemSelected = (event, item) => {
    if (item){
        axios.get(addSuffixToBackendURL("users/" + item.user_id), 
        {headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` }})
        .then((res) => {
           const user: SearchBarUser = {
                label: res.data.vorname + " " + res.data.nachname + " " + res.data.email,
                user_id: res.data.user_id,
              }
              console.log(user)
            setSelectedUser(user)
        })
        
    };
    };

    const handleInputChange = (event, newInputValue) => {
        setInputValue(newInputValue);
    };



    useEffect(() => {
    const token = localStorage.getItem("accessToken");
    axios.get(addSuffixToBackendURL("users/current/single"), {headers: { Authorization: `Bearer ${token}` }})
    .then((res) => {
        setCurrentUser({
            label: res.data.vorname + " " + res.data.nachname + " " + res.data.email,
            user_id: res.data.user_id,
        })
        axios.get(addSuffixToBackendURL("users/chat/history"), {headers: { Authorization: `Bearer ${token}` }})
            .then((res2) => {
            setUserHistory(res2.data)
            const uniqueIDs = getUniqueUsers(res2.data, res.data.user_id)
            axios.get(addSuffixToBackendURL("users"), {headers: { Authorization: `Bearer ${token}` }})
                .then((res3) => {
                setUsers(reduceUsers(res3.data))
                setHistoryUsers(reduceUsers(filterSearchBarUsers(res3.data, uniqueIDs)))
                })
                    .catch((err) => {
                    if (err.response && err.response.status === 401 || err.response.status === 403) {
                        console.log("Unauthorized  oder kein Admin", err.response.data)
                        navigate("/login")
                    }
                    console.log(err.response.data)
                    })
            })
                .catch((err) => {
                if (err.response && err.response.status === 401 || err.response.status === 403) {
                    console.log("Unauthorized  oder kein Admin", err.response.data)
                    navigate("/login")
                }
                console.log(err.response.data)
                })
    })
    .catch((err) => {
        if (err.response && err.response.status === 401 || err.response.status === 403) {
        console.log("Unauthorized  oder kein Admin", err.response.data)
        navigate("/login")
        }
        console.log(err.response.data)
    })

    }, []) 



  if (currentUser === null) {
    return <div>loading...</div>
  }

  return (
      <div>
        <Grid container>
            <Grid item xs={12} >
                <Typography variant="h5" className="header-message">Chat</Typography>
            </Grid>
        </Grid>
        <Grid container component={Paper} className={classes.chatSection}>
            <Grid item xs={3} className={classes.borderRight500}>
                <List>
                <SideUser user={currentUser} current={true}/>
                </List>
                <Divider />
                <Grid item xs={12} style={{padding: '10px'}}>
                <Autocomplete
                            freeSolo
                            onChange={handleSearchItemSelected}
                            inputValue={inputValue}
                            onInputChange={handleInputChange}
                            options={users}
                            classes={{
                                paper: classes.paper, // Apply your custom styles to the dropdown
                                option: classes.option, // Apply custom styles to each option
                            }}
                            getOptionLabel={(option) => option.label}
                            renderInput={(params) => <TextField {...params} label={<SearchIcon />} />}
                            sx={{ width: 200 }}
                        />

                </Grid>
                <Divider />
                <List>
                    {
                        historyUsers.map((user) => {
                            return <SideUser user={user} current={false} selectedUser={selectedUser} activeSetter={setSelectedUser}/>
                        })
                    }
                </List>
            </Grid>
            {selectedUser != null &&
            <Messages classes={classes} current_user={currentUser} selectedUser={selectedUser}
            history={individualHistory} historySetter={setIndividualHistory}/>
            }   
        </Grid>
      </div>
  );
}

export default Chat;