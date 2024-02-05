import axios from 'axios';
import { addSuffixToBackendURL } from './networking_utils';
import { SmartmeterData } from '../components/netzbetreiber/dashboard/NetzbetreiberSmartmeterOverview';

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
    const today = new Date().toISOString().split('T')[0];

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
            link.setAttribute('download', `${today}_${filename}`);
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


export const convertToCSV = (data: Array<Object>) => {
    const csvRows = [];
    // Get the headers
    const headers = Object.keys(data[0]);
    csvRows.push(headers.join(','));

    // Loop over the rows
    for (const row of data) {
        const values = headers.map(header => {
            const escaped = ('' + row[header]).replace(/"/g, '\\"');
            return `"${escaped}"`;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
};

