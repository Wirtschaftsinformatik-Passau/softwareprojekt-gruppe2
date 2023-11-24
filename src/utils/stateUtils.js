const handleInputChange = setter => event => {
    setter(event.target.value);
};

export default handleInputChange;