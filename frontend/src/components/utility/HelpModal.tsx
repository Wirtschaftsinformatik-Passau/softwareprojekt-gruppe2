import { type } from "os";
import React from "react";
import { useNavigate } from "react-router-dom";

type HelpModalProps = {
    modalCloserState: (arg: boolean) => void,
}

const HelpModal: React.FC<HelpModalProps> = ({modalCloserState}) => {
    const itemStyle = "text-md border-b-2 cursor:pointer"
    const navigate = useNavigate()

    return (
        <div 
        onMouseLeave={() => modalCloserState(false)}
        className={`fixed top-14 md:top-16 right-16 bg-white px-6 py-4 rounded-xl grid grid-rows-2 gap-4`}>
                <h3 className={itemStyle}>
                     Hilfe
                </h3>
                <h3 className={itemStyle}
                onClick={() => navigate("/registration")}>
                    Home
                </h3>
                <h3 className={itemStyle}>
                    Kontakt
                </h3>
           </div>
   
    )
}

export default HelpModal;
