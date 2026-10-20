import React, { useState } from "react";
import { Shield, Mail, LogOut, Settings, User, LogOut as LogOutIcon, Folder, TrendingUp } from "lucide-react";
import { supabase } from "../lib/supabase";

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

const SettingsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState({
    name: "",
    email: "",
    targetRole: "",
    experienceLevel: "",
  });

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get current user
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) {
        setError("No authenticated session. Please sign in first.");
        setIsLoading(false);
        return;
      }

      // Call backend API to update profile
      const response = await fetch(`${API_BASE_URL}/api/v1/profile/`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: profile.name,
          target_role: profile.targetRole,
          experience_level: profile.experienceLevel,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save profile");
      }

      // Refresh profile data from Supabase auth
      const { data: { user: updatedUser} } = await supabase.auth.getUser();
      if (updatedUser) {
        setProfile({
          name: updatedUser.user_metadata?.full_name || profile.name,
          email: updatedUser.email || profile.email,
          targetRole: updatedUser.user_metadata?.target_role || profile.targetRole,
          experienceLevel: updatedUser.user_metadata?.experience_level || profile.experienceLevel,
        });
      }

      setIsLoading(false);
    } catch (err: any) {
      console.error("Profile save error:", err);
      setError(err.message || "Failed to save profile");
    }
  };

  const handleChangePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    if (profile.newPassword !== profile.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }

    try {
      // Get current user
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) {
        setError("No authenticated session");
        setIsLoading(false);
        return;
      }

      // Call backend API to change password
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/change-password`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_password: profile.currentPassword,
          new_password: profile.newPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to change password");
      }

      setIsLoading(false);
    } catch (err: any) {
      console.error("Change password error:", err);
      setError(err.message || "Failed to change password");
    }
  };

  // Initialize profile from Supabase auth on mount
  useEffect(() => {
    const initProfile = async () => {
      const { data: { user} } = await supabase.auth.getUser();
      if (user) {
        setProfile({
          name: user.user_metadata?.full_name || "",
          email: user.email || "",
          targetRole: user.user_metadata?.target_role || "",
          experienceLevel: user.user_metadata?.experience_level || "",
        });
      }
    };

    initProfile();
  }, []);

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">
          Settings
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="card p-6 border border-border">
            <h2 className="text-font-medium text-fg-primary mb-3">
              Profile
            </h2>

            <form className="space-y-4">
              <div>
                <label className="block text-fg-secondary text-sm mb-2">
                  Full Name
                </label>
                <input
                  value={profile.name}
                  onChange={(e) =>
                    setProfile({ ...profile, name: e.target.value })
                  }
                  className="input w-full"
                  aria-label="Full name"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-fg-secondary text-sm mb-2">
                  Email
                </label>
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
                <label className="block text-fg-secondary text-sm mb-2">
                  Target Role
                </label>
                <select
                  value={profile.targetRole}
                  onChange={(e) =>
                    setProfile({ ...profile, targetRole: e.target.value })
                  }
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
                <label className="block text-fg-secondary text-sm mb-2">
                  Experience Level
                </label>
                <select
                  value={profile.experienceLevel}
                  onChange={(e) =>
                    setProfile({ ...profile, experienceLevel: e.target.value })
                  }
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
            <h2 className="text-font-medium text-fg-primary mb-3">
              Account Security
            </h2>

            <p className="text-fg-secondary text-sm mb-4">
              Manage your account security and privacy settings.
            </p>

            <form onSubmit={handleChangePasswordSubmit} className="space-y-4">
              <div>
                <label className="block text-fg-secondary text-sm mb-2">
                  Current Password
                </label>
                <input
                  type="password"
                  value={profile.currentPassword}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      currentPassword: e.target.value,
                    })
                  }
                  className="input w-full"
                  aria-label="Current password"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-fg-secondary text-sm mb-2">
                  New Password
                </label>
                <input
                  type="password"
                  value={profile.newPassword}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      newPassword: e.target.value,
                    })
                  }
                  className="input w-full"
                  aria-label="New password"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-fg-secondary text-sm mb-2">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={profile.confirmPassword}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      confirmPassword: e.target.value,
                    })
                  }
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
          <h2 className="text-font-medium text-fg-primary mb-4">
            Data Management
          </h2>

          <div className="space-y-3">
            <button
              onClick={() => {
                // Would trigger profile deletion with auth confirmation
                alert("Resume deletion would require authentication and confirmation");
              }}
              className="flex items-center gap-2 text-fg-secondary hover:text-red-600 transition-colors"
            >
              <Icon className="h-4 w-4" /> Delete Resumes
            </button>

            <button
              onClick={() => {
                // Would trigger interview history deletion
                alert("Interview history deletion would require authentication");
              }}
              className="flex items-center gap-2 text-fg-secondary hover:text-red-600 transition-colors"
            >
              <Icon className="h-4 w-4" /> Delete Interview History
            </button>

            <button
              onClick={() => {
                // Would sign out and account deletion
                alert("Account deletion - contact support for assistance");
              }}
              className="flex items-center gap-2 text-fg-secondary hover:text-red-600 transition-colors"
            >
              <Icon className="h-4 w-4" /> Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;