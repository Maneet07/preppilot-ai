import React, { useEffect, useState } from "react";
import { Loader2, Square, TrendingUp, BarChart2, User, Shield, FileText, Folder, Microscope, Code, Flag, Heart, CheckCircle, LogOut } from "lucide-react";
import "../index.css";

interface ResumeAnalysis {
  id: number;
  overall_score: number | null;
  created_at: string;
}

interface InterviewSession {
  id: number;
  interview_type: string;
  target_role: string | null;
  status: string;
  overall_score: number | null;
  created_at: string;
}

// Icon components mapped by interview type
const getIconClass = (type: string) => {
  switch (type) {
    case 'technical':
      return Microscope;
    case 'behavioral':
      return User;
    case 'mixed':
      return Heart;
    default:
      return User;
  }
};

const DashboardPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dashboard metrics
  const [metrics, setMetrics] = useState<{
    total_interviews: number;
    completed_interviews: number;
    average_score: number;
    resume_readiness_score: number | null;
    total_resumes: number;
    total_analyses: number;
  }>({
    total_interviews: 0,
    completed_interviews: 0,
    average_score: 0,
    resume_readiness_score: null,
    total_resumes: 0,
    total_analyses: 0,
  });
  
  // Recent resume analyses
  const [recentAnalyses, setRecentAnalyses] = useState<ResumeAnalysis[]>([]);
  
  // Recent interview sessions
  const [recentInterviews, setRecentInterviews] = useState<InterviewSession[]>([]);

  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      try {
        // In a real implementation, this would fetch from the API
        // For now, simulate API calls
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate dashboard data
        setMetrics({
          total_interviews: 5,
          completed_interviews: 3,
          average_score: 7.5,
          resume_readiness_score: 72,
          total_resumes: 2,
          total_analyses: 2,
        });
        
        setRecentAnalyses([
          { id: 1, overall_score: 72, created_at: "2024-01-15" },
          { id: 2, overall_score: 85, created_at: "2024-01-10" },
        ]);
        
        setRecentInterviews([
          { id: 1, interview_type: "technical", target_role: "Software Engineer", status: "completed", overall_score: 8.5, created_at: "2024-01-20" },
          { id: 2, interview_type: "behavioral", target_role: "Product Manager", status: "completed", overall_score: 7.2, created_at: "2024-01-18" },
          { id: 3, interview_type: "technical", target_role: "Software Engineer", status: "completed", overall_score: 9.0, created_at: "2024-01-15" },
        ]);
     
      } catch (err) {
        setError(err.message || "Failed to load dashboard data");
      } finally {
        setIsLoading(false);
      }
    };
    
    loadDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-fg-muted">
          <Loader2 className="h-8 w-8 animate-spin mr-3" />
          Loading dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-100 border-red-400 text-red-700 rounded-md mb-6">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      <header className="flex items-center justify-between border-b border-border bg-white px-4 py-3">
        <h1 className="text-2xl font-bold text-fg-primary">
          Dashboard
          <span className="text-fg-secondary text-sm">Welcome back</span>
        </h1>
      </header>

      <main className="p-6 flex flex-col gap-6">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card p-6 border border-border">
            <div className="flex items-start gap-3">
              <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-fg-secondary text-sm">Total Interviews</p>
                <p className="text-3xl font-bold text-fg-primary">{metrics.total_interviews}</p>
              </div>
            </div>
          </div>
          
          <div className="card p-6 border border-border">
            <div className="flex items-start gap-3">
              <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-fg-secondary text-sm">Completed Interviews</p>
                <p className="text-3xl font-bold text-fg-primary">{metrics.completed_interviews}</p>
              </div>
            </div>
          </div>
          
          <div className="card p-6 border border-border">
            <div className="flex items-start gap-3">
              <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-fg-secondary text-sm">Average Score</p>
                <p className="text-3xl font-bold text-fg-primary">{metrics.average_score}</p>
              </div>
            </div>
          </div>
          
          <div className="card p-6 border border-border">
            <div className="flex items-start gap-3">
              <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-fg-secondary text-sm">Resume Readiness</p>
                <p className="text-3xl font-bold text-fg-primary">{metrics.resume_readiness_score || 0}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Resume Analyses */}
        <div className="card p-6 border border-border">
          <h2 className="font-medium text-fg-primary mb-4">Recent Resume Analyses</h2>
          {recentAnalyses.length === 0 && <p className="text-fg-muted text-sm">No resume analyses yet. Upload and analyze a resume to see your readiness score.</p>}
          
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentAnalyses.map((analysis) => (
              <div key={analysis.id} className="flex items-center justify-between p-3 rounded-md transition-colors hover:bg-muted">
                <span className="text-fg-secondary text-sm">{analysis.created_at}</span>
                <span className="font-medium text-accent-primary">{analysis.overall_score || 0}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Interview Sessions */}
        <div className="card p-6 border border-border">
          <h2 className="font-medium text-fg-primary mb-4">Recent Interview Sessions</h2>
          {recentInterviews.length === 0 && <p className="text-fg-muted text-sm">No interview sessions yet. Start a mock interview to get started.</p>}
          
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentInterviews.map((session) => (
              <div key={session.id} className="flex items-center justify-between p-3 rounded-md transition-colors hover:bg-muted">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-fg-secondary" />
                  <span className="text-fg-secondary text-sm">{session.interview_type}</span>
                  <span className="ml-2 text-fg-secondary text-sm">{session.target_role || "Unknown Role"}</span>
                </div>
                <span className="text-accent-primary font-medium">{session.overall_score || 0}/10</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;