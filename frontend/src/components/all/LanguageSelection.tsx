import React from "react";
// @ts-ignore
import usa from "../../assets/vereinigte-staaten.png"
// @ts-ignore
import german from "../../assets/deutschland.png"

// eslint-disable-next-line react/prop-types

type LanguageSelectionProps = {
    closeSetter: (arg: boolean) => void
}
const LanguageSelection: React.FC<LanguageSelectionProps> = ({closeSetter}) => {
    return (
        <div className="flex flex-row gap-2">
            <img
            src={german}
            className="h-12 w-12 cursor:pointer"
            onClick={() => {
                closeSetter(false)
            }}
            />
            <img
                src={usa}
                className="h-12 w-12 cursor:pointer"
                onClick={() => {
                    closeSetter(false)
                }}
            />
        </div>
    )
}

export default LanguageSelection