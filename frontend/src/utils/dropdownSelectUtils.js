const customStyles = {
    control: (provided, state) => ({
        ...provided,
        borderRadius: '0.375rem',
        marginTop: "4px",
        boxShadow: state.isFocused ? "#6A994E" : 'none',
        backgroundColor: "transparent",
        borderWidth: '2px',
        "&:hover": {
            borderColor:"#6A994E"
        }
    }),
    option: (provided, state) => ({
       ...provided,
       color:"black",
       backgroundColor: state.isSelected ? "transparent" : "transparent",
        '&:active': {
            backgroundColor: "#6A994E",
        },
    })
}

export default customStyles