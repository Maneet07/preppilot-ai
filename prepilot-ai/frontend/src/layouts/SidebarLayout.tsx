import React from "react";
import { Icon, Menu, Search, User, Logout, Settings, Home, Resume, Job, Microscope, Code, Layout, History, Flag, UserPlus, Settings as SettingsIcon, LogOut } from "lucide-react";
import "./index.css";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  onClick?: () => void;
}

interface SidebarProps {
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  currentPage: string;
  setCurrentPage: (page: string) => void;
  userInitials: string;
  onLogout: () => void;
}

const SidebarLayout: React.FC<SidebarProps> = ({
  isCollapsed,
  setIsCollapsed,
  currentPage,
  setCurrentPage,
  userInitials,
  onLogout,
}) => {
  const navItems: NavItem[] = [
    { label: "Dashboard", href: "/", icon: Home, currentPage: "dashboard" },
    { label: "Resume Analyzer", href: "/resume-analyzer", icon: Resume, currentPage: "resume" },
    { label: "Job Description Analyzer", href: "/job-analyzer", icon: Job, currentPage: "job" },
    { label: "Mock Interviews", href: "/mock-interviews", icon: Microscope, currentPage: "interviews" },
    { label: "Technical Practice", href: "/technical-practice", icon: Code, currentPage: "practice" },
    { label: "Coding Practice", href: "/coding-practice", icon: Code, currentPage: "coding" },
    { label: "Interview History", href: "/interview-history", icon: History, currentPage: "history" },
    { label: "Reports", href: "/reports", icon: Flag, currentPage: "reports" },
    { label: "Profile", href: "/profile", icon: UserPlus, currentPage: "profile" },
    { label: "Settings", href: "/settings", icon: SettingsIcon, currentPage: "settings" },
  ];

  return (
    <aside 
      className="flex h-screen w-16 flex-shrink-0 bg-white border-r border-border min-h-screen flex-col overflow-y-auto"
      onClick={() => setIsCollapsed(!isCollapsed)}
    >
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="h-6 w-6 text-accent-primary" />
          <span className="font-medium text-fg-primary text-sm">PrepPilot AI</span>
        </div>
        <button
          onClick={(() => setIsCollapsed(true))}
          className="text-fg-muted hover:text-fg-primary transition-colors"
          aria-label="Open sidebar"
        >
          <Icon className="h-4 w-4" />
        </button>
      </div>

      <nav className="flex-1 flex flex-col pt-2 space-y-1">
        {navItems.map((item, index) => (
          <button
            key={index}
            onClick={(e) => {
              e.stopPropagation();
              setCurrentPage(item.currentPage);
              setIsCollapsed(true);
            }}
            className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-all hover:bg-border ${currentPage === item.currentPage 
              ? "bg-accent-muted text-accent-primary" 
              : "text-fg-muted hover:bg-muted"}
            }
            aria-label={item.label}
          >
            <item.icon className="h-4 w-4" />
            <span className="hidden md:block">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-3 border-t border-border mt-auto">
        <div className="flex items-center gap-3">
          <Icon 
            className="h-5 w-5 text-fg-muted"
            title={userInitials}
          />
          <span className="text-xs text-fg-muted capitalize">{userInitials}</span>
        </div>
        <button
          onClick={onLogout}
          className="mt-2 w-full text-left text-xs text-fg-muted hover:text-fg-primary transition-colors"
        >
          Logout
        </button>
      </div>
    </aside>
  );
};

export default SidebarLayout;