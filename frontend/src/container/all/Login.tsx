import React from 'react';
// @ts-ignore
import panelImg from "../../assets/solar_login2.jpg";

import RegistryHeader from "../../components/all/RegistryHeader";
const Login = () => {
   return(
       <div className="flex justify-start items-center flex-col h-screen bg-green-200">
           <RegistryHeader/>
           <div className=" relative w-full h-full">
               <img src={panelImg} alt="solar panel"
                    className="w-full h-full object-cover"/>
               <RegistryHeader/>
               <div className="absolute flex flex-col justify-center items-center top-0 left-0 right-0 bottom-0">
                    <form>
                        <div className="flex flex-col gap-5 justify-center items-center rounded-2xl bg-white bg-opacity-80 py-20 px-5">
                            <h1 className="text-5xl text-blue-500">
                                GreenEcoHub
                            </h1>
                            <input type="text" className="py-2.5 px.2.5 bg-transparent border-0 focus:outline-none
                            border-b-2 border-b-gray-500 placeholder-gray-500 text-md focus:border-blue-500" placeholder={"E-Mail"}/>
                            <input type="password" className="py-2.5 px.2.5 bg-transparent border-0 focus:outline-none
                            border-b-2 border-b-gray-500 placeholder-gray-500 text-md focus:border-blue-500" placeholder={"Password"}/>
                           <div className="grid grid-cols-2 gap-5 w-9/12">
                               <button className="bg-gray-500 rounded-lg px-10 py-1 text-white">
                                   Passwort vergessen?
                               </button>
                            <button className="bg-blue-500 rounded-lg px-10 py-1 text-white">
                                Login!
                            </button>
                           </div>
                        </div>
                    </form>
               </div>
           </div>
       </div>
   )
}

export default Login;