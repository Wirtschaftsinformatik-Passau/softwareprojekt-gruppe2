// @ts-ignore
// eslint-disable-next-line no-unused-vars
import {React, useState} from "react";
import Charts from "../../components/admin/Charts";
import AdminNavbar from "../../components/admin/AdminNavbar";
import RegistryHeader from "../../components/all/registration/RegistryHeader";

const  AdminDashboard = () => {
    const [effect, setEffect] = useState("")

    return (
        <>
        
        <div className="flex flex-row bg-white- w-full h-screen">
        <RegistryHeader color="red-200"/>
            <AdminNavbar/>
            <div className="flex flex-col h-full w-full mt-16 md:mt-20">
                <div className="flex justify-center">
                    <div className="bg-white p-10 rounded-3xl bg-opacity-70">
                        <h1 className="text-3xl">
                        Willkommen im Admin-Dashboard!
                        </h1>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4  sm:gap-6 py-10 sm:py-20">
                <div className="bg-white p-10 rounded-3xl bg-opacity-70 px-20 cursor-pointer">
                        <h1 className="text-xl border-b-2 hover:border-color2">
                        Log Datei Verwaltung
                        </h1>
                    </div>
                    <div className="bg-white p-10 rounded-3xl bg-opacity-70 px-20 cursor-pointer">
                        <h1 className="text-xl border-b-2 hover:border-color2">
                       Nutzerverwaltung
                        </h1>
                    </div>
                </div>
            </div>

        </div>
        </>
    )

}

export default AdminDashboard;