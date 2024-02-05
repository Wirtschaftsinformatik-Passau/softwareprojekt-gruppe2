import { type } from "os";
import React from "react";
import { useNavigate } from "react-router-dom";
import { navigateToHome } from "../../utils/navigateUtils";
import { Nutzerrolle, User } from "../../entitities/user";

type HelpModalProps = {
    modalCloserState: (arg: boolean) => void,
    nutzerrolle: User | null,
    navigateFN: () => void
}

const HelpModal: React.FC<HelpModalProps> = ({modalCloserState, nutzerrolle=null, navigateFN=null}) => {
    const itemStyle = "text-md border-b-2 cursor:pointer"
    const navigate = useNavigate()

    return (
        <div 
        onMouseLeave={() => modalCloserState(false)}
        className={`fixed top-16 md:top-18 right-16 bg-white px-6 py-4 rounded-xl grid grid-rows-2 gap-4 text-color1`}>
                {nutzerrolle != undefined &&
                <button>
                <h3 className={itemStyle}
                onClick={
                    nutzerrolle === undefined ? () => navigate("/login") :
                    () => navigateToHome(nutzerrolle, navigateFN)}>
                    Home
                </h3>
                </button>
}
                <button>
                <h3 className={itemStyle} onClick={() => navigate("/impressum")}>
                    Impressum
                </h3>
                </button>
           </div>
   
    )
}

export default HelpModal;
