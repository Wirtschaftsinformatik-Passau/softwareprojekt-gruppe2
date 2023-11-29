import React, {useState} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSolarPanel } from '@fortawesome/free-solid-svg-icons';
import { faGlobe } from '@fortawesome/free-solid-svg-icons';

import LanguageSelection from "../LanguageSelection.js";

const RegistryHeader = () => {
    const [iconAction, setIconAction] = useState(false)

   return(
       <div className="absolute top-0 left-0 bg-white bg-opacity-80 w-full h-12 py-2 md:h-16 sm:h-10 flex justify-between items-center px-4">

       <div className="flex flex-row gap-8">

           <FontAwesomeIcon
               icon={faSolarPanel}
               className="text-5xl text-color2 hover:text-color2"

           />
           <h1 className="text-5xl text-color2">
               GreenEcoHub
           </h1>

       </div>
           {
               iconAction ?
                   <LanguageSelection
                    closeSetter={setIconAction}
                   />:
           <FontAwesomeIcon
               icon={faGlobe}
               className="text-5xl text-color2 hover:text-blue-500 hover:animate-bounce cursor:pointer"
               onClick={() => {
                   console.log("over")
                   setIconAction(true)
               }}
           />

           }
    </div>
   )
}

export default RegistryHeader;