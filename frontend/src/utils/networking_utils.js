import axios from "axios";

export const addSuffixToBackendURL = (suffix) => {
    return import.meta.env.VITE_BACKEND_URL + suffix;
}

export const setStateofResponse = async (setter, endpoint, headers = {}) => {
    try {
        const response = await axios.get(addSuffixToBackendURL(endpoint), {headers: headers});
        setter(response.data);
    } catch (err) {
        console.log(err.response.data);
    }
};