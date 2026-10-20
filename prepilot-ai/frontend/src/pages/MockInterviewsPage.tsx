import React, { useState } from "react";
import { Loader2, Microscope, MessageCircle, LogOut, Calendar, MenuSquare, Shield, Settings, TrendingUp } from "lucide-react";
import "../index.css";

const MockInterviewsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const interviewTypes = ["technical", "behavioral", "mixed"];

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Mock Interviews</h1>
        
        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">Start New Interview</h2>
          
          <form className="space-y-4">
            <div>
              <label className="block text-fg-secondary text-sm mb-2">Interview Type</label>
              <select className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary">
                <option value="technical">Technical</option>
                <option value="behavioral">Behavioral</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>
            
            <div>
              <label className="block text-fg-secondary text-sm mb-2">Target Role</label>
              <input
                placeholder="e.g., Software Engineer"
                className="input w-full"
                aria-label="Target role"
              />
            </div>
            
            <div>
              <label className="block text-fg-secondary text-sm mb-2">Experience Level</label>
              <select className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary">
                <option value="junior">Junior (0-2 years)</option>
                <option value="mid">Mid (2-5 years)</option>
                <option value="senior">Senior (5+ years)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-fg-secondary text-sm mb-2">Difficulty</label>
              <select className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isLoading ? "Starting..." : "Generate Questions"}
            </button>
          </form>
        </div>

        <div>
          <h2 className="text-font-medium text-fg-primary mb-4">Recent Sessions</h2>
          <p className="text-fg-secondary text-sm">No recent sessions yet. Start a new mock interview above.</p>
        </div>
      </div>
    </div>
  );
};

export default MockInterviewsPage;