import Dialog from '@mui/material/Dialog';
import { Box, Button, TextField , Typography, useTheme} from "@mui/material";
import DialogContent from '@mui/material/DialogContent';
import { tokens } from "../../../utils/theme";
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import { TransitionProps } from '@mui/material/transitions';
import React from 'react';
import ModalWrapper from '../../utility/ModalWrapper';
import axios from 'axios';
import { addSuffixToBackendURL } from '../../../utils/networking_utils';

interface MyDialogProps {
    open: boolean;
    handleClose: () => void;
}

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
      children: React.ReactElement<any, any>;
    },
    ref: React.Ref<unknown>,
  ) {
    return <Slide direction="up" ref={ref} {...props} />;
  });

const MyDialogComponent: React.FC<MyDialogProps> = ({open, handleClose}) => {
    const [email, setEmail] = React.useState("")
    const theme = useTheme();  
    const [successModalText, setSuccessModalText] = React.useState("Wir haben dir eine Email mit einem Link zum Zurücksetzen deines Passworts geschickt. Bitte überprüfe auch deinen Spam-Ordner.")
    const colors = tokens(theme.palette.mode);
    const [successModalIsOpen, setSuccessModalIsOpen] = React.useState(false);

    const passwordRequest = () => {
        const accessToken = localStorage.getItem("accessToken")
        axios.post(addSuffixToBackendURL("users/request-password-reset"), {
            email: email
        }, {headers: {Authorization: `Bearer ${accessToken}`}}).then((response) => {
            console.log(response.data)
            setSuccessModalIsOpen(true)
            
        })
        .catch((error) => {
            setSuccessModalText("Es ist ein Fehler aufgetreten. Bitte versuche es später erneut.")
            setSuccessModalIsOpen(true)
        })
    }


    return (
        <React.Fragment>
        <Dialog open={open} onClose={handleClose} 
        
        TransitionComponent={Transition}
        keepMounted>
            <div className='bg-white'>
            <DialogContent sx={{
            
    }}>     
            <ModalWrapper modalCloserState={handleClose} rows={2}>

                    {successModalIsOpen ?
                    <Typography variant="h5" sx={{
                        color: colors.color1[400],
                        fontWeight: "bold",
                        textAlign: "center",
                    }}>
                        {successModalText}
                    </Typography>
                    :
                    <>
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="email"
                        placeholder="E-Mail eingeben"
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <Button variant="contained" sx= {{
                        backgroundColor: `${colors.color1[400]} !important`,
                        color: theme.palette.background.default,
                        padding: "10px 20px",
                        width: "100%",
                    }}  onClick={passwordRequest}>
                            Email versenden!
                    </Button>
                    </>
}
                    
            </ModalWrapper>
            </DialogContent>
          
            </div>
            
        </Dialog>
    
        </React.Fragment>
    )
}

export default MyDialogComponent;