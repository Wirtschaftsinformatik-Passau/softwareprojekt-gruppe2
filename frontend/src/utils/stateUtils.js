import { red } from "@material-ui/core/colors";
import { addSuffixToBackendURL } from "./networking_utils";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const handleInputChange = setter => event => {
    setter(event.target.value);
};

export const setStateOtherwiseRedirect = (setter, endpoint, redirectFn, headers={}) => {
    axios.get(addSuffixToBackendURL(endpoint), {headers: headers})
    .then(response => {
        console.log("reuududdudududududuu")
        setter(response.data);
        console.log(response.data)
    })
    .catch((err) => {
        if (err.response.status === 401) {
          redirectFn("/login")
        }
        else if (err.response.status === 403) {
          redirectFn("/login");

        }
        console.log(err.response.data)
      })
}


export default handleInputChange;