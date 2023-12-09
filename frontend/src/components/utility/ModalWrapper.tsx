import React from "react";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { tokens } from '../../utils/theme';
import { useTheme } from "@mui/material/styles";

type ModalWrapperProps = {
    modalCloserState: (arg: boolean) => void,
    rows: number,
    children: React.ReactNode
}

const ModalWrapper: React.FC<ModalWrapperProps> = ({modalCloserState, children, rows}) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    return (
        <div className={`relativep-8 rounded-2xl grid grid-rows-${rows} gap-4`} style={{background: theme.palette.background.default}}>
            {children}     
        <FontAwesomeIcon 
            className='absolute top-1 right-2 cursor-pointer'
            style={{color: colors.grey[300]}}
            onClick={() => modalCloserState(false)}
            icon={faTimes} />                
        </div>
    )
}


export default ModalWrapper;