import Dialog from '@mui/material/Dialog';
import { Box, Button, TextField , useTheme} from "@mui/material";
import DialogContent from '@mui/material/DialogContent';
import { tokens } from "../../../utils/theme";
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import { TransitionProps } from '@mui/material/transitions';
import React from 'react';
import ModalWrapper from '../../utility/ModalWrapper';

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
    const [passwordWindow, setPasswordWindow] = React.useState(false)

    const handleCloseExtended = () => {
        handleClose()
        setPasswordWindow(false)
    }

    return (
        <React.Fragment>
        <Dialog open={open} onClose={handleCloseExtended} 
        
        TransitionComponent={Transition}
        keepMounted>
            <div className='bg-white'>
            <DialogTitle>{"Use Google's location service?"}</DialogTitle>
            <DialogContent sx={{
            
    }}>     
            <ModalWrapper modalCloserState={handleCloseExtended} rows={2}>
            {passwordWindow ? (
                <>
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="password"
                        onChange={(event) => (console.log("fff"))}
                        placeholder="Passwort eingeben"
                    />
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="password"
                        onChange={(event) => (console.log("fff"))}
                        placeholder="Passwort erneut eingeben"
                    />
                    <Button
                        onClick={handleCloseExtended}
                        sx={{
                            backgroundColor: "#6a994e",
                            color: "#fff",
                            borderRadius: "10px",
                            }}>
                            
                        Email versenden!
                    </Button>
                </>
            ) : (
                <>
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="email"
                        placeholder="E-Mail eingeben"
                        onChange={(event) => (console.log("fff"))}
                    />
                    <Button
                        onClick={() => setPasswordWindow(true)}
                        sx={{
                            backgroundColor: "#6a994e",
                            color: "#fff",
                        }}>
                            
                        Email versenden!
                    </Button>
                </>
            )}
            </ModalWrapper>
            </DialogContent>
          
            </div>
            
        </Dialog>
    
        </React.Fragment>
    )
}

export default MyDialogComponent;