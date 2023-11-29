import React from 'react';
import {faCircleXmark} from "@fortawesome/free-solid-svg-icons/faCircleXmark";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

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
            <div className="bg-white p-8 rounded-xl grid grid-rows-2 gap-4">
                <div className={"flex flex-row justify-center border-b-2"}>
                    <FontAwesomeIcon
                        icon={faCircleXmark}
                        className="text-2xl text-red-700 px-5"
                    />
                    <h1 className="text-center text-xl">
                    Passwort Falsch!
                </h1>
                    <FontAwesomeIcon
                        icon={faCircleXmark}
                        className="text-2xl text-red-700 px-5"
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <button className="p-2 bg-gray-500 text-white rounded-xl">Passwort vergessen!</button>
                    <button
                        onClick={handleErneutVersuchen}
                        className="p-2 bg-color2 text-white rounded-xl">Erneut versuchen!</button>
                </div>
            </div>

        </div>
    )
}

export default LoginModal;