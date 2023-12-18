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