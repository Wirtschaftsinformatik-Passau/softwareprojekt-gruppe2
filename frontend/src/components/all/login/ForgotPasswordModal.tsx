import Dialog from '@mui/material/Dialog';
import { Box, Button, TextField , useTheme} from "@mui/material";
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import { tokens } from "../../../utils/theme";
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import { TransitionProps } from '@mui/material/transitions';
import React from 'react';
import ModalWrapper from '../../utility/ModalWrapper';

type ModalProps = {
    modalCloserState: (arg: boolean) => void,
}

const ForgotPasswordModal: React.FC<ModalProps> = ({modalCloserState}) => {
    const [email, setEmail] = React.useState("")
    const [password1, setPassword1] = useState("")
    const [password2, setPassword2] = useState("")
    const [passwordScreen, setPasswordScreen] = React.useState(false)
    const [registryModal, setRegistryModal] = React.useState(false)
    const checkPasswordEquality = () => password1 === password2 && password1 !== "" && password2 !== ""

    const passwordButton = (event: any) => {
        event.preventDefault()

        if (checkPasswordEquality()) {
            modalCloserState(false)
        } else {
            setRegistryModal(true)
        }
    }

    return (
    <div className="fixed left-0 top-0 right-0 bottom-0 bg-black bg-opacity-50 flex justify-center items-center">
        <ModalWrapper modalCloserState={modalCloserState} rows={2}>
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
        </ModalWrapper>
    </div>
    )
};

export  default ForgotPasswordModal;