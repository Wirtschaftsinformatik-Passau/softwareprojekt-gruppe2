import React from 'react';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCircleXmark} from "@fortawesome/free-solid-svg-icons/faCircleXmark";

import ModalWrapper from '../../utility/ModalWrapper';

type RegistryModalProps = {
    modalCloserState: (arg: boolean) => void,
    content: string

}

// @ts-ignore
const RegistryModal: React.FC<RegistryModalProps> = ({modalCloserState, content}) => {
    const handleOk = (event: any):void => {
        event.preventDefault()
        modalCloserState(false)
    }

    return (
        <div className="fixed top-0 left-0 right-0 bottom-0 flex justify-center items-center bg-black bg-opacity-50">
           <ModalWrapper modalCloserState={modalCloserState} rows={2}>
                <div className={"flex flex-row justify-center border-b-2"}>
                    <FontAwesomeIcon
                        icon={faCircleXmark}
                        className="text-2xl text-red-700 px-4 mt-0.5"
                    />
                    <h1 className="text-center text-xl">
                        {content}
                    </h1>
                    
                </div>
                <div className="flex flex-row justify-center">
                    <button onClick={handleOk}
                            className="p-2 bg-gray-500 text-white rounded-xl px-10">
                        Ok!
                    </button>
            </div>

            </ModalWrapper>
            </div>
    )
}


export default RegistryModal;