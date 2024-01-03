export const convertToTimeOnly = (data) => {
    return data.map(item => {
        const date = new Date(item.x);
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return {
            ...item,
            x: `${hours}:${minutes}` 
        };
    });
};


export const convertToDateOnly = (data) => {
    return data.map(item => {
        const date = new Date(item.x);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0'); // getMonth() is zero-based
        const day = date.getDate().toString().padStart(2, '0');
        return {
            ...item,
            x: `${year}-${month}-${day}`
        };
    });
};

export const formatDate = (dateString) => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // getMonth() is zero-based
    const day = date.getDate().toString().padStart(2, '0');

    return `${year}-${month}-${day}`;
}

export const dateFormater = (date) => {
    const dateObject = new Date(date);
    const year = dateObject.getFullYear();
    const month = dateObject.getMonth() + 1;
    const day = dateObject.getDate();
    const hours = dateObject.getHours();
    const minutes = dateObject.getMinutes();
    const dateString = day + "." + month + "." + year + " " + hours + ":" + minutes;
    return dateString;
}