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

export const dateFormater = (date, usformat=false) => {
    const dateObject = new Date(date);
    const year = dateObject.getFullYear();
    const month = dateObject.getMonth() + 1;
    const day = dateObject.getDate();
    const hours = dateObject.getHours();
    const minutes = dateObject.getMinutes();
    const minutesString = minutes < 10 ? "0" + minutes : minutes;
    const hoursString = hours < 10 ? "0" + hours : hours;
    const dateString = day + "." + month + "." + year + " " + hoursString + ":" + minutesString
    if (usformat) {
        return month + "/" + day + "/" + year + " " + hoursString + ":" + minutesString;
    }
    return dateString;
}

export const formatTime = (dateString) => {
    const date = new Date(dateString);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`
}