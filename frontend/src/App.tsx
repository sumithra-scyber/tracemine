import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import ConnectGmailPage from "./pages/ConnectGmailPage";
import ScanProgressPage from "./pages/ScanProgressPage";
import DashboardPage from "./pages/DashboardPage";
import GhostAccountsPage from "./pages/GhostAccountsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/connect" element={<ConnectGmailPage />} />
        <Route path="/scan" element={<ScanProgressPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/ghosts" element={<GhostAccountsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
