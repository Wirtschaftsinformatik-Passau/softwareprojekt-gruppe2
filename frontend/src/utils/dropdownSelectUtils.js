const customStyles = {
    control: (provided, state) => ({
        ...provided,
        borderRadius: '0.375rem',
        marginTop: "4px",
        borderColor: state.isFocused ? "rgb(59 130 246)" : "rgb(156 163 175)",
        boxShadow: state.isFocused ? '0 0 0 1px blue' : 'none',
        backgroundColor: "transparent",
        borderWidth: '2px',
        "&:hover": {
            borderColor: state.isFocused ? "rgb(59 130 246)" : "gray",
        }
    }),
    option: (provided, state) => ({
       ...provided,
       color:"black",
       backgroundColor: state.isSelected ? "transparent" : "transparent",
        '&:active': {
            backgroundColor: 'green',
        },
    })
}

export default customStyles