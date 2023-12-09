import Dialog from '@mui/material/Dialog';
import { Box, Button, TextField , Typography, useTheme} from "@mui/material";
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


    return (
        <React.Fragment>
        <Dialog open={open} onClose={handleClose} 
        
        TransitionComponent={Transition}
        keepMounted>
            <div className='bg-white'>
            <DialogTitle>{""}</DialogTitle>
            <DialogContent sx={{
            
    }}>     
            <ModalWrapper modalCloserState={handleClose} rows={2}>

                <>
                    <Typography>
                        Passwort falsch!
                    </Typography>
                    <Button
                        onClick={handleClose}
                        sx={{
                            backgroundColor: "#6a994e",
                            color: "#fff",
                        }}>
                        Ok!
                    </Button>
                </>
        
            </ModalWrapper>
            </DialogContent>
          
            </div>
            
        </Dialog>
    
        </React.Fragment>
    )
}

export default MyDialogComponent;