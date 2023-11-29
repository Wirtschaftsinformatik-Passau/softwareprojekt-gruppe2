import React from 'react';
import { useNavigate,NavigateFunction } from "react-router-dom";

import LoginModal from "../../components/all/login/LoginModal";
import ForgotPasswordModal from "../../components/all/login/ForgotPasswordModal";

// @ts-ignore
import panelImg from "../../assets/solar_login2.jpg";

import RegistryHeader from "../../components/all/registration/RegistryHeader";
const Login = () => {
    const navigate: NavigateFunction = useNavigate();
    const [modalisOpen, setModalIsOpen] = React.useState(false);
    const [forgotPasswordModalIsOpen, setForgotPasswordModalIsOpen] = React.useState(false);
    const [password, setPassword] = React.useState("")
    const [email, setEmail] = React.useState("")
    const checkLogin = (event: any) => {
        event.preventDefault()
        setModalIsOpen(true)
    }
    const updatePassword = (event: any) => {
        setPassword(event.target.value)
    }
    const updateEmail = (event: any) => {
        setEmail(event.target.value)
    }

    const handlePasswordForgot = (event: any) => {
        event.preventDefault()
        setForgotPasswordModalIsOpen(true)
    }
   return(
       <div className="flex justify-start items-center flex-col h-screen">

           <div className=" relative w-full h-full">
               <img src={panelImg} alt="solar panel"
                    className="w-full h-full object-cover"/>
               <div className="absolute flex flex-col justify-center items-center top-0 left-0 right-0 bottom-0">
                   <RegistryHeader/>
                   <form>
                        <div className="flex flex-col gap-5 justify-center items-center rounded-2xl bg-white bg-opacity-80 py-20">
                            <h1 className="text-5xl text-color2">
                                GreenEcoHub
                            </h1>
                            <input type="text" className="py-2.5 px.2.5 bg-transparent border-0 focus:outline-none
                            border-b-2 border-b-gray-500 placeholder-gray-500 text-md focus:border-color2" placeholder={"E-Mail"}/>
                            <input type="password" className="py-2.5 px.2.5 bg-transparent border-0 focus:outline-none
                            border-b-2 border-b-gray-500 placeholder-gray-500 text-md focus:border-color2" placeholder={"Password"}/>
                           <div className="grid grid-cols-3 gap-5 w-9/12">
                               <button className="bg-gray-500 rounded-lg px-10 py-1 text-white"
                               onClick={() => navigate("/registration")}>
                                   Registrieren
                               </button>
                               <button
                                   onClick={handlePasswordForgot}
                                   className="bg-gray-500 rounded-lg px-10 py-1 text-white">
                                   Passwort vergessen?
                               </button>
                            <button className="bg-color2 rounded-lg px-10 py-1 text-white"
                                    onClick={checkLogin}
                            >
                                Login!
                            </button>
                           </div>
                            {modalisOpen && (<LoginModal modalCloserState={setModalIsOpen}/>)}
                            {forgotPasswordModalIsOpen && (<ForgotPasswordModal modalCloserState={setForgotPasswordModalIsOpen}/>)}
                        </div>
                    </form>
               </div>
           </div>
       </div>
   )
}

export default Login;