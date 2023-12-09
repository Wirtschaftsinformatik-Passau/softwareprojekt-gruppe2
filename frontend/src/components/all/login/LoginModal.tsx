import React from 'react';
import {faCircleXmark} from "@fortawesome/free-solid-svg-icons/faCircleXmark";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

import ModalWrapper from '../../utility/ModalWrapper';

type LoginModalProps = {
    modalCloserState: (arg: boolean) => void,
}

// @ts-ignore
const LoginModal: React.FC<LoginModalProps> = ({modalCloserState}) => {
    const handleErneutVersuchen = (event: any):void => {
        event.preventDefault()
        modalCloserState(false)
    }

 
    return (
        <div className="fixed top-0 left-0 right-0 bottom-0 flex justify-center items-center bg-black bg-opacity-50">
           <ModalWrapper modalCloserState={modalCloserState} rows={2}>
                <div className={"flex flex-row justify-center border-b-2"}>
                    <FontAwesomeIcon
                        icon={faCircleXmark}
                        className="text-2xl text-red-700 px-2 mt-0.5"
                    />
                    <h1 className="text-center text-xl">
                    Passwort oder E-Mail Adresse falsch!
                </h1>
                 
                </div>
                <div className="grid grid-cols-1 gap-4">
            
                    <button
                        onClick={handleErneutVersuchen}
                        className="p-2 bg-color2 text-white rounded-xl">Erneut versuchen!</button>
                </div>
            </ModalWrapper>
            </div>
        
    )
}

export default LoginModal;