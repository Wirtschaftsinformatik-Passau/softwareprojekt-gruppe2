// eslint-disable-next-line no-unused-vars
import React from "react";
import {Routes, Route} from "react-router-dom";
import Registration from "./container/all/Registration.tsx"
import AdminDashboard from "./container/admin/AdminDashboard.tsx";
import Login from "./container/all/Login.tsx"

const App = () => {
    return (
        <Routes>
            <Route path="/registration" element={<Registration/>}/>
            <Route path="/login" element={<Login/>}/>
            <Route path="*" element={<div><h1>hello</h1></div>}/>
            <Route path="/admin" element={<AdminDashboard/>}/>
        </Routes>
    )
}

export default App
