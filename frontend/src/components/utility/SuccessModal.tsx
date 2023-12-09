import Dialog from '@mui/material/Dialog';
import { Box, Button, TextField , Typography, useTheme} from "@mui/material";
import DialogContent from '@mui/material/DialogContent';
import { tokens } from '../../utils/theme';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import { TransitionProps } from '@mui/material/transitions';
import React from 'react';
import ModalWrapper from './ModalWrapper';
import { useNavigate } from 'react-router-dom';

interface MyDialogProps {
    text: string
    open: boolean;
    handleClose: () => void;
    navigationGoal?: string;

}

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
      children: React.ReactElement<any, any>;
    },
    ref: React.Ref<unknown>,
  ) {
    return <Slide direction="up" ref={ref} {...props} />;
  });

const SuccessModal: React.FC<MyDialogProps> = ({text, open, handleClose, navigationGoal}) => {
    const navigate = useNavigate()
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    const handleCloseExtened = () => {  
        handleClose()
        if(navigationGoal){
            navigate(navigationGoal)
        }
    }

    return (
        <React.Fragment>
        <Dialog open={open} onClose={handleCloseExtened} 
        
        TransitionComponent={Transition}
        keepMounted>
            <div style={{background: theme.palette.background.default}}>
            <DialogTitle>{""}</DialogTitle>
            <DialogContent sx={{
    }}>     
            <ModalWrapper modalCloserState={handleClose} rows={2}>

                <>
                    <Typography sx={{color: colors.grey[300]}}>
                       {text}
                    </Typography>
                    <Button
                        onClick={handleCloseExtened}
                        sx={{
                            backgroundColor: colors.color1[500],
                            color: theme.palette.background.default,
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

export default SuccessModal