import { useState } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import LogsExplorer from "./pages/LogsExplorer.jsx";
import ClusterView from "./pages/ClusterView.jsx";
import ReviewQueue from "./pages/ReviewQueue.jsx";
import ExportHealth from "./pages/ExportHealth.jsx";

const TITLES = {
  "/": "Dashboard",
  "/logs": "Logs",
  "/clusters": "Clusters",
  "/review": "Review Queue",
  "/export": "Export",
};

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const title = TITLES[location.pathname] || "Flywheel";

  return (
    <div className="lg:flex min-h-screen">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 min-w-0">
        {/* mobile topbar */}
        <header className="lg:hidden sticky top-0 z-20 flex items-center gap-3 border-b border-line bg-paper/90 backdrop-blur px-4 py-3">
          <button
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
            className="p-1.5 -ml-1.5 rounded hover:bg-ink/5"
          >
            <span className="block w-5 h-0.5 bg-ink mb-1" />
            <span className="block w-5 h-0.5 bg-ink mb-1" />
            <span className="block w-5 h-0.5 bg-ink" />
          </button>
          <div className="text-sm font-semibold">{title}</div>
        </header>

        <main className="p-4 sm:p-6 max-w-full overflow-x-hidden">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/logs" element={<LogsExplorer />} />
            <Route path="/clusters" element={<ClusterView />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/export" element={<ExportHealth />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
