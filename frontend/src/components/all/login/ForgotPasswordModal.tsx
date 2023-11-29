import React, {useState} from "react";
import handleInputChange from "../../../utils/stateUtils";
import RegistryModal from "../RegistryModal";


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
        <div className="bg-white p-8 rounded-xl grid grid-rows-2 gap-8 p-12">
            {passwordScreen ? (
                <>
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="password"
                        onChange={(event) => handleInputChange(setPassword1)}
                        placeholder="Passwort eingeben"
                    />
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="password"
                        onChange={(event) => handleInputChange(setPassword2)}
                        placeholder="Passwort erneut eingeben"
                    />
                    <button
                        onClick={passwordButton}
                        className="p-2 bg-color2 text-white rounded-xl px-10">
                        Bestätigen!
                    </button>
                    {registryModal && (<RegistryModal modalCloserState={setRegistryModal} content={"Passwörter stimmen nicht überein!"}/>)}
                </>
            ) : (
                <>
                    <input
                        className="block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none focus:outline-none focus:ring-0 focus:border-color2"
                        type="email"
                        placeholder="E-Mail eingeben"
                        onChange={(event) => handleInputChange(setEmail)}
                    />
                    <button
                        onClick={() => setPasswordScreen(true)}
                        className="p-2 bg-color2 text-white rounded-xl px-10">
                        Email versenden!
                    </button>
                </>
            )}
        </div>
    </div>
    )
};

export  default ForgotPasswordModal;