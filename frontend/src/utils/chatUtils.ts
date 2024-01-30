import Search from "@mui/icons-material/Search";
import { User } from "../entitities/user";
import { addSuffixToBackendURL } from "./networking_utils";
import axios from "axios";

export interface ExtendedUser extends User {
    user_id: number;
}

export interface SearchBarUser  {
    label: string;
    user_id: number;
}

export interface ChatHistory {
    nachricht_id: number;
    sender_id: number;
    empfaenger_id: number;
    nachricht_inhalt: string;
    timestamp: string;
}

export const  reduceUsers = (users: ExtendedUser[]) : SearchBarUser[]=> {
    return users.map((user) => {
        const label = `${user.vorname} ${user.nachname} (${user.email})`;
        return { label: label, user_id: user.user_id };
    });
}

export const getUniqueUsers = (history: ChatHistory[], ignoreID: number) : number[] => {
    const uniqueUsers = new Set<number>();
    history.forEach((message) => {
        uniqueUsers.add(message.sender_id);
        uniqueUsers.add(message.empfaenger_id);
    });
    uniqueUsers.delete(ignoreID);
    return Array.from(uniqueUsers);
}

export const filterSearchBarUsers = (users: SearchBarUser[], user_ids: number[]) : SearchBarUser[] => {
    const filteredUsers =  users.filter((user) => user_ids.includes(user.user_id));
    console.log(user_ids);
    return filteredUsers;
}


export const setAndRequestConversationHistory = async (user_id: number, other_user_id: number, setter: any) => {
    const accessToken = localStorage.getItem("accessToken");
    const senderUrl = addSuffixToBackendURL(`users/chat/history?user_id=${user_id}&other_user_id=${other_user_id}`);
    axios.get(senderUrl, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    }).then((response) => {
        const data = response.data;
        data.sort((a: ChatHistory, b: ChatHistory) => {
            return a.timestamp > b.timestamp ? 1 : -1;
        });
        setter(data);
    }).catch((error) => {
        console.log(error);
    });
    

}
