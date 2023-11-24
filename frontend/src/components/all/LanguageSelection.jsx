import React from "react";
import usa from "../../assets/vereinigte-staaten.png"
import german from "../../assets/deutschland.png"

// eslint-disable-next-line react/prop-types
const LanguageSelection = ({closeSetter}) => {
    return (
        <div className="flex flex-row gap-2">
            <img
            src={german}
            className="h-12 w-12 hover:animate-bounce cursor:pointer"
            onClick={() => {
                closeSetter(false)
            }}
            />
            <img
                src={usa}
                className="h-12 w-12 hover:animate-bounce cursor:pointer"
                onClick={() => {
                    closeSetter(false)
                }}
            />
        </div>
    )
}

export default LanguageSelection