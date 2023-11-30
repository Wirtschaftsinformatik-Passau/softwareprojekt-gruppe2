// eslint-disable-next-line no-unused-vars
import {React, useState} from "react";
import {Routes, Route, Navigate} from "react-router-dom";
import Registration from "./container/all/Registration.tsx"
import AdminDashboard from "./container/admin/AdminDashboard.tsx";
import Login from "./container/all/Login.tsx"

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    return (
        <Routes>
            <Route path="/registration" element={<Registration/>}/>
            <Route path="/login" element={<Login/>}/>
            <Route path="/admin" element={<AdminDashboard/>}/>
            <Route path="*" element={
                isLoggedIn ? <Navigate to="/admin"/> : <Navigate to="/login"/>
            }/>
        </Routes>
    )
}

export default App
