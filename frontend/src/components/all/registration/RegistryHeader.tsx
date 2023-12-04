import React, {useState} from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSolarPanel } from '@fortawesome/free-solid-svg-icons';
import { faGlobe } from '@fortawesome/free-solid-svg-icons';
import { faQuestion } from '@fortawesome/free-solid-svg-icons';

import LanguageSelection from "../LanguageSelection.js";
import HelpModal from '../../utility/HelpModal.js';

type RegistryHeaderProps = {
    color: string,
}

const RegistryHeader: React.FC<RegistryHeaderProps> = ({color}) => {
    const colorValue = color || "white"
    const [iconAction, setIconAction] = useState(false)
    const [help, setHelp] = useState(false)

   return(
       <div className={`absolute top-0 left-0 bg-${colorValue} bg-opacity-80 w-full h-14 py-2 md:h-16 sm:h-10 flex justify-between items-center px-4`}>

       <div className="flex flex-row gap-8">

           <FontAwesomeIcon
               icon={faSolarPanel}
               className="text-5xl text-color2 hover:text-color2"

           />
           <h1 className="text-5xl text-color2">
               GreenEcoHub
           </h1>

       </div>
       
        <div className='grid grid-cols-2 gap-2'>
            <div className=''>
                <button>
        <FontAwesomeIcon
       icon={faQuestion}
       onClick={() => setHelp(true)}
       className='text-5xl text-color2 hover:text-blue-500 hover:animate-bounce cursor:pointer'
       />
       </button>
       {help && (<HelpModal modalCloserState={setHelp}/>)}
       </div>
           {
               iconAction ?
                   <LanguageSelection
                    closeSetter={setIconAction}
                   />:
                   <button>
           <FontAwesomeIcon
               icon={faGlobe}
               className="text-5xl text-color2 hover:text-blue-500 hover:animate-bounce cursor:pointer"
               onClick={() => {
                   console.log("over")
                   setIconAction(true)
               }}
           />
           </button>
           }
           </div>
    </div>
   )
}

export default RegistryHeader;