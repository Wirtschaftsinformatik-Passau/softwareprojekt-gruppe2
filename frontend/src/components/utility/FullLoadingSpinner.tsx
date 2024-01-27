import Dialog from '@mui/material/Dialog';
import { Box, Button, TextField , Typography, useTheme} from "@mui/material";
import DialogContent from '@mui/material/DialogContent';
import { tokens } from '../../utils/theme';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import CircularProgress from '@mui/material/CircularProgress';
import { TransitionProps } from '@mui/material/transitions';
import React from 'react';
import ModalWrapper from './ModalWrapper';
import { useNavigate } from 'react-router-dom';





const FullLoadingSpinner = () => {
    const navigate = useNavigate()
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

  
    return (
        <React.Fragment>
        
            <div style={{
                background: theme.palette.background.default,
                opacity:"50%"}}>
            
            <Box display="flex" justifyContent="center" alignItems="center" height="300px">
             <CircularProgress />
              </Box>
        
          
            </div>
            
    
        </React.Fragment>
    )
}

export default FullLoadingSpinner