// @ts-ignore
// eslint-disable-next-line no-unused-vars
import {React, useState} from "react";
import Charts from "../../components/admin/Charts";
import AdminNavbar from "../../components/admin/AdminNavbar";

const  AdminDashboard = () => {
    const [effect, setEffect] = useState("")

    return (
        <div className="flex flex-row bg-blue-950 w-full h-screen">
            <AdminNavbar/>
            <div className="grid grid-rows-4 gap-10 h-full w-full">
                <div className="w-full grid grid-cols-2 gap-10">
                    <Charts/>
                </div>
                <div className="w-full grid grid-cols-2 gap-10 ">
                    <div>
                        <Charts/>
                    </div>
                    <div className="grid grid-cols-2 gap-5">
                        <div className={`bg-green-400 rounded-xl ${effect}`}
                            onMouseEnter={() => setEffect("animate-pulse")}
                             onMouseLeave={() => setEffect("")}>
                            dd
                        </div>
                        <div className={"bg-green-600 rounded-l-lg"}>
                            dd
                        </div>
                    </div>
                </div>
            </div>

        </div>
    )

}

export default AdminDashboard;