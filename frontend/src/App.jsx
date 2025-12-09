import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Scan from "./pages/Scan";
import BatchScan from "./pages/BatchScan";
import LiveScan from "./pages/LiveScan";
import AdminDashboard from "./pages/AdminDashboard";
import AdminLogin from "./pages/AdminLogin";
import NotFound from "./pages/NotFound";
import DamagedIC from "./pages/DamagedIC";

function App() {
  return (
    <>
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/scan/batch" element={<BatchScan />} />
          <Route path="/scan/live" element={<LiveScan />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="*" element={<NotFound />} />
          <Route path="/admin/damaged-ic" element={<DamagedIC />} />

        </Routes>
      </main>
    </>
  );
}

export default App;
