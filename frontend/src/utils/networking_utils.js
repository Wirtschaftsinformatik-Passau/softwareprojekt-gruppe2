export const addSuffixToBackendURL = (suffix) => {
    return import.meta.env.VITE_BACKEND_URL + suffix;
}
