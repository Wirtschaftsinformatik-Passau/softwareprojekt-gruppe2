// @ts-ignore
import {React, SetStateAction, useState} from "react";
// @ts-ignore
import Select from 'react-select';
import axios from "axios";
// @ts-ignore
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css'; // Import the CSS for the DatePicker

//TODO: Add validation for all fields

import "../../index.css"

import RegistryHeader from "../../components/all/registration/RegistryHeader";
// @ts-ignore
import solarGif from '../../assets/solar-pannels-wind-power-plant-outside.jpg'
import customStyles from "../../utils/dropdownSelectUtils.js";
import handleInputChange from "../../utils/stateUtils.js";
import RegistryModal from "../../components/all/registration/RegistryModal";
import {IUser, User, Nutzerrolle, UserDropDownOption} from "../../entitities/user"
import { Iadresse, Adresse } from "../../entitities/adress";
import { addSuffixToBackendURL } from "../../utils/networking_utils";


const Registration = () => {
    const inputStyle = "block py-2.5 sm:py-1 px-0 w-full placeholder-gray-500 text-md text-black bg-transparent border-0 border-b-2 sm:border-b-1 border-gray-400 appearance-none  focus:outline-none focus:ring-0 focus:border-color2"
    const [email, setEmail] = useState("")
    const [password1, setPassword1] = useState("")
    const [password2, setPassword2] = useState("")
    const [selectedOption, setSelectedOption] = useState(Nutzerrolle.Kunde);
    const [telefon, setTelefon] = useState("")
    const [gebDatum, setGebDatum] = useState(new Date())
    const [plz, setPlz] = useState("")
    const [strasse, setStrasse] = useState("")
    const [stadt, setStadt] = useState("")
    const [titel, setTitel] = useState("")
    const [nachname, setNachname] = useState("")
    const [vorname, setVorname] = useState("")
    const [hausnr, setHausnr] = useState("")
    const [contentModalisOpen, setContentModalisOpen] = useState(false);
    const [passwordModalisOpen, setPasswordModalIsOpen] = useState(false);
    const [emailModalisOpen, setEmailModalIsOpen] = useState(false);


    const roleOptions: Array<UserDropDownOption> = [
        {
            label: "Admin",
            value: Nutzerrolle.Admin
        },
        {
            value: Nutzerrolle.Netzbetreiber,
            label: "Netzbetreiber"
        },
        {
            value: Nutzerrolle.Kunde,
            label: "Kunder"
        },
        {
            value: Nutzerrolle.Berater,
            label: "Berater"
        }
    ]

    const checkPasswordEquality = () => password1 === password2;
    const checkRequiredFields = () => (vorname !== "") && (nachname !== "") && (stadt !== "") && (strasse !== "") &&
        (plz !== "") && (selectedOption != null) && (email !== "") && (password1 !== "") && (password2 !== "")

    const buttonHandler = () => {
        if (!checkRequiredFields()) {
            setContentModalisOpen(true)
            return
        }

        if (!checkPasswordEquality()) {
            setPasswordModalIsOpen(true)
            return
        }

        const adresse: Iadresse = new Adresse(strasse, Number(hausnr), Number(plz), stadt, "Deutschland")
        axios.post(addSuffixToBackendURL("users/adresse"), adresse
        )
            .then((response) => {
                const adresse_id = response.data.adresse_id
                if (response.status === 201) {
                    console.log("Adresse erfolgreich gespeichert")
                    const user: IUser = new User(vorname, nachname, telefon, email, password1, selectedOption.value, gebDatum.toDateString(), adresse_id, titel)
         
                    axios.post(addSuffixToBackendURL("users/registration"), user)
                        .then((response) => {
                            if (response.status === 201) {
                                console.log("User erfolgreich gespeichert")
                            }
                        })
                        .catch((error) => {
                            if (error.response && error.response.status === 422) {
                        
                                console.log("Server Response on Error 422:", error.response.data);
                            } else if (error.response && error.response.status === 409) {
                                //setEmailModalIsOpen(true)
                             
                               }
                                  else {
                                console.log(error);
                            }
                        }
                        )
                }
            })
            .catch((error) => {
                if (error.response && error.response.status === 422) {
                    console.log("Server Response on Error 422:", error.response.data);
                } else {
                    console.log(error);
                }
            })

    
    }
    const handleRoleSelect = (option: any) => {
        setSelectedOption(option);
    }
    
    const validKeyForPayment = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "Backspace",
        "Tab"
      ];

    return (
        <div className="flex justify-start items-center flex-col h-screen">
            <div className="relative top-0 left-0 w-full h-full">

                <img
                src={solarGif}
                alt={"loading"}
                className="w-full h-full object-cover"
                />

                <div className="absolute top-0 left-0 bottom-0 right-0 flex flex-col justify-center items-center">
                    <RegistryHeader/>
                    <div className="justify-self-center bg-white bg-opacity-80 flex flex-col justify-center
                    items-center px-5 pt-5 sm:p-10 max-w-screen-lg sm:max-w-screen-sm md:max-w-screen-md rounded-3xl py-4">
                        <form className="justify-self-center">
                            <div className="grid grid-rows-4 gap-10 md:gap-5">
                                <div className="grid grid-cols-3 gap-10 md:gap-5">
                                    <div>
                                        <input
                                            type="text"
                                            className={inputStyle}
                                            placeholder="Titel"
                                            onChange={handleInputChange(setTitel)} />
                                    </div>
                                    <div className="rounded-md">
                                        <input
                                            type="text"
                                            className={inputStyle}
                                            placeholder="Vorname*"
                                            onChange={handleInputChange(setVorname)} />
                                    </div>
                                    <div className="rounded-md">
                                        <input
                                            type="text"
                                            className={inputStyle}
                                            placeholder="Nachname*"
                                            onChange={handleInputChange(setNachname)} />
                                    </div>
                                </div>
                                <div className="grid grid-cols-3 gap-10 md:gap-5">
                                    <div>
                                        <input
                                            type="text"
                                            className={inputStyle}
                                            placeholder="Straße*"
                                            onChange={handleInputChange(setStrasse)} />
                                    </div>
                                    <div className="flex gap-10 md:gap-5 rounded-md">
                                        <div className="flex-1 min-w-0">
                                            <input
                                                type="text"
                                                className={inputStyle}
                                                placeholder="Hausnr.*"
                                                onKeyDown={(e) => {
                                                    if (!validKeyForPayment.includes(e.key)) {
                                                      e.preventDefault();
                                                    }}}
                                                onChange={handleInputChange(setHausnr)} />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <input
                                                 onKeyDown={(e) => {
                                                    if (!validKeyForPayment.includes(e.key)) {
                                                      e.preventDefault();
                                                    }}}
                                                type="text"
                                                className={inputStyle}
                                                placeholder="PLZ*"
                                                onChange={handleInputChange(setPlz)} />
                                        </div>
                                    </div>
                                    <div className="rounded-md">
                                        <input
                                            type="text"
                                            className={inputStyle}
                                            placeholder="Stadt*"
                                            onChange={handleInputChange(setStadt)} />
                                    </div>
                                </div>
                                <div className="grid grid-cols-3 gap-10 md:gap-5">
                                    <div className="rounded-md mt-2">
                                        <DatePicker
                                            className={`text-base ${inputStyle}`}
                                            placeholderText="Geburtstag*"
                                            showIcon
                                            selected={gebDatum}
                                            onChange={(date: Date) => setGebDatum(date)}
                                        />

                                    </div>
                                    <div className="rounded-md">
                                        <input
                                            type="text"
                                            className={`${inputStyle}`}
                                            placeholder="Telefon*"
                                            onKeyDown={(e) => {
                                                if (!validKeyForPayment.includes(e.key)) {
                                                  e.preventDefault();
                                                }}}
                                            onChange={handleInputChange(setTelefon)} />
                                    </div>
                                    <div className="rounded-md">
                                        <Select
                                            className="rounded-md"
                                        placeholder="Nutzerrolle*"
                                            onChange={handleRoleSelect}
                                            value={selectedOption}
                                        options={roleOptions}
                                            styles={customStyles}
                                        />

                                    </div>
                                </div>
                                <div className="grid grid-cols-3 gap-10 md:gap-5">
                                    <div>
                                        <input
                                            type="email"
                                            className={inputStyle}
                                            placeholder="Email*"
                                            onChange={handleInputChange(setEmail)} />
                                    </div>
                                    <div className="rounded-md">
                                        <input
                                            type="password"
                                            className={inputStyle}
                                            placeholder="Passwort*"
                                            onChange={handleInputChange(setPassword1)} />
                                    </div>
                                    <div className="rounded-md">
                                        <input
                                            type="password"
                                            className={inputStyle}
                                            placeholder="Passwort wiederholen*"
                                            onChange={handleInputChange(setPassword2)} />
                                    </div>
                                </div>
                                <div className="flex justify-center items-center h-full">
                                <button
                                type="button"
                                className="mt-5 bg-color2 rounded-xl text-md text-white w-1/3"
                                onClick={buttonHandler}>
                                    Registrieren!
                                </button>
                                </div>
                            </div>
                        </form>
                    </div>
                    {contentModalisOpen && (<RegistryModal modalCloserState={setContentModalisOpen} content={"Bitte alle benötigten Felder ausfüllen!"}/>)}
                    {passwordModalisOpen && (<RegistryModal modalCloserState={setPasswordModalIsOpen} content={"Passwörter stimmen nicht überein!"}/>)}
                    {emailModalisOpen && (<RegistryModal modalCloserState={setEmailModalIsOpen} content={"Email bereits vergeben!"}/>)}
                </div>
            </div>
        </div>
    )
}

export default Registration;