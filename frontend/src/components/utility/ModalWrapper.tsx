import React from "react";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

type ModalWrapperProps = {
    modalCloserState: (arg: boolean) => void,
    rows: number,
    children: React.ReactNode
}

const ModalWrapper: React.FC<ModalWrapperProps> = ({modalCloserState, children, rows}) => {
    return (
        <div className={`relative bg-white p-8 rounded-xl grid grid-rows-${rows} gap-4`}>
            {children}     
        <FontAwesomeIcon 
            className='absolute top-1 right-2 text-black cursor-pointer'
            onClick={() => modalCloserState(false)}
            icon={faTimes} />                
        </div>
    )
}


export default ModalWrapper;