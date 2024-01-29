import axios from 'axios';
import { addSuffixToBackendURL } from './networking_utils';

export interface ReportURL {
    endpoint: string;
    filename: string;
} 

const defaultUrls: ReportURL[] = [
    { endpoint: "admin/download_reports_dashboard", filename: "dashboard.csv" },
    { endpoint: "admin/download_reports_vertrag", filename: "vertrag.csv" },
    { endpoint: "admin/download_reports_rechnungen", filename: "rechnungen.csv" },
    { endpoint: "admin/download_reports_energieausweise", filename: "energieausweise.csv" }
]; 

export const getAllReports = async (urls: ReportURL[] = defaultUrls) => {
    const accessToken = localStorage.getItem("accessToken");

    for (const { endpoint, filename } of urls) {
        const url = addSuffixToBackendURL(endpoint);
        try {
            const response = await axios.get(url, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
                responseType: 'blob',
            });

            const file = new Blob(
                [response.data],
                { type: 'text/csv' } 
            );

            // Build a URL from the file
            const fileURL = URL.createObjectURL(file);

            // Create a temporary link element and download the file
            const link = document.createElement('a');
            link.href = fileURL;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();

            // Clean up and revoke the URL
            document.body.removeChild(link);
            URL.revokeObjectURL(fileURL);
        } catch (error) {
            console.error('Error downloading file:', error);
        }
    }
};