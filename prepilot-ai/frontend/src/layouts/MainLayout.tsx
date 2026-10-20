import React, { useState } from "react";
import { Menu, Search, User, LogOut, LogOut as LogOutIcon } from "lucide-react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import "./index.css";
import SidebarLayout from "./SidebarLayout";

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const navigate = useNavigate();

  const handlePageChange = (page: string) => {
    // Navigate based on page
    navigate(`/${page}`);
  };

  return (
    <Router>
      <div className="min-h-screen bg-bg-primary flex flex-col">
        <header 
          className="flex items-center justify-between border-b border-border bg-bg-secondary px-4 py-3"
        >
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="md:hidden p-2 rounded-md hover:bg-border transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          <div className="flex items-center gap-4">
            <Search className="h-5 w-5 text-fg-muted" />
            <input 
              type="search" 
              placeholder="Search..." 
              className="input flex-1"
              aria-label="Search"
            />
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-fg-muted" />
              <span className="text-sm text-fg-secondary">User</span>
              <svg className="h-4 w-4 text-fg-muted rotate-180" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 5a3 3 0 0 1 3 3h2a3 3 0 0 1 3 3v2a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3zm3 2h-2V5h2v3zM7 3V1a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2H7V3zm3 11h-2v2h2v2h-2v-2zm-3-8V1H5v2h6v6H5v2h6v-2H5zm2 5h2v2h-2v-2zm-5 5h2v2h-2v-2zm3 4h-2v6h2v-6zm2-5a2 2 0 1 1 0-4 2 2 0 0 1 0 4z" />
              </svg>
            </div>
          </div>
        </header>

        <SidebarLayout
          isCollapsed={isSidebarCollapsed}
          setIsCollapsed={setIsSidebarCollapsed}
          currentPage="dashboard"
          setCurrentPage={handlePageChange}
          userInitials="UA"
          onLogout={() => alert("Logout clicked")}
        />

        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </Router>
  );
};

export default MainLayout;