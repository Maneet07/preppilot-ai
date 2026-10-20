import React, { useState } from "react";
import { Shield, Mail, LogOut, Settings, User, LogOut as LogOutIcon, Folder, TrendingUp } from "lucide-react";
import "../index.css";

const SettingsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState({
    name: "",
    email: "",
    targetRole: "",
    experienceLevel: "",
  });

  const [changePassword] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    
    // Would call backend API to update profile
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const handleChangePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    if (changePassword.newPassword !== changePassword.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }
    
    // Would call backend API to change password
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Settings</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="card p-6 border border-border">
            <h2 className="text-font-medium text-fg-primary mb-3">Profile</h2>
            
            <form className="space-y-4">
              <div>
                <label className="block text-fg-secondary text-sm mb-2">Full Name</label>
                <input
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  className="input w-full"
                  aria-label="Full name"
                  placeholder="John Doe"
                />
              </div>
              
              <div>
                <label className="block text-fg-secondary text-sm mb-2">Email</label>
                <input
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  className="input w-full"
                  aria-label="Email"
                  placeholder="you@example.com"
                  disabled
                />
              </div>
              
              <div>
                <label className="block text-fg-secondary text-sm mb-2">Target Role</label>
                <select
                  value={profile.targetRole}
                  onChange={(e) => setProfile({ ...profile, targetRole: e.target.value })}
                  className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
                >
                  <option value="">Select target role</option>
                  <option value="Software Engineer">Software Engineer</option>
                  <option value="Product Manager">Product Manager</option>
                  <option value="Data Scientist">Data Scientist</option>
                  <option value="DevOps Engineer">DevOps Engineer</option>
                  <option value="Tech Lead">Tech Lead</option>
                </select>
              </div>
              
              <div>
                <label className="block text-fg-secondary text-sm mb-2">Experience Level</label>
                <select
                  value={profile.experienceLevel}
                  onChange={(e) => setProfile({ ...profile, experienceLevel: e.target.value })}
                  className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
                >
                  <option value="">Select experience level</option>
                  <option value="junior">Junior (0-2 years)</option>
                  <option value="mid">Mid (2-5 years)</option>
                  <option value="senior">Senior (5+ years)</option>
                </select>
              </div>
              
              <button
                type="submit"
                disabled={isLoading}
                className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {isLoading ? "Saving..." : "Save Changes"}
              </button>
            </form>
          </div>
          
          <div className="card p-6 border border-border">
            <h2 className="text-font-medium text-fg-primary mb-3">Account Security</h2>
            
            <p className="text-fg-secondary text-sm mb-4">
              Manage your account security and privacy settings.
            </p>
            
            <form onSubmit={handleChangePasswordSubmit} className="space-y-4">
              <div>
                <label className="block text-fg-secondary text-sm mb-2">Current Password</label>
                <input
                  type="password"
                  value={changePassword.currentPassword}
                  onChange={(e) => setChangePassword({ ...changePassword, currentPassword: e.target.value })}
                  className="input w-full"
                  aria-label="Current password"
                  placeholder="••••••••"
                />
              </div>
              
              <div>
                <label className="block text-fg-secondary text-sm mb-2">New Password</label>
                <input
                  type="password"
                  value={changePassword.newPassword}
                  onChange={(e) => setChangePassword({ ...changePassword, newPassword: e.target.value })}
                  className="input w-full"
                  aria-label="New password"
                  placeholder="••••••••"
                />
              </div>
              
              <div>
                <label className="block text-fg-secondary text-sm mb-2">Confirm New Password</label>
                <input
                  type="password"
                  value={changePassword.confirmPassword}
                  onChange={(e) => setChangePassword({ ...changePassword, confirmPassword: e.target.value })}
                  className="input w-full"
                  aria-label="Confirm password"
                  placeholder="••••••••"
                />
              </div>
              
              <button
                type="submit"
                disabled={isLoading}
                className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {isLoading ? "Changing..." : "Change Password"}
              </button>
            </form>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-border">
          <h2 className="text-font-medium text-fg-primary mb-4">Data Management</h2>
          
          <div className="space-y-3">
            <button
              onClick={() => alert("Resume deletion initiated")}
              className="flex items-center gap-2 text-fg-secondary hover:text-red-600 transition-colors"
            >
              <Icon className="h-4 w-4" />
              Delete Resumes
            </button>
            
            <button
              onClick={() => alert("Interview history deletion initiated")}
              className="flex items-center gap-2 text-fg-secondary hover-text-red-600 transition-colors"
            >
              <Icon className="h-4 w-4" />
              Delete Interview History
            </button>
            
            <button
              onClick={() => alert("Account deletion initiated - contact support")}
              className="flex items-center gap-2 text-fg-secondary hover:text-red-600 transition-colors"
            >
              <Icon className="h-4 w-4" />
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;