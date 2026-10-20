import React, { useEffect, useState } from "react";
import { Loader2, Square, TrendingUp, BarChart2, User, Shield, FileText, Folder, Microscope, Code, Flag, Heart, CheckCircle, LogOut } from "lucide-react";
import { supabase } from "../lib/supabase";

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

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

interface DashboardMetrics {
  total_interviews: number;
  completed_interviews: number;
  average_score: number;
  resume_readiness_score: number | null;
  total_resumes: number;
  total_analyses: number;
}

interface RecentResumeAnalysis {
  id: number;
  overall_score: number | null;
  created_at: string;
}

interface RecentInterviewSession {
  id: number;
  interview_type: string;
  target_role: string | null;
  status: string;
  overall_score: number | null;
  created_at: string;
}

const DashboardPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [metrics, setMetrics] = useState<DashboardMetrics>({
    total_interviews: 0,
    completed_interviews: 0,
    average_score: 0,
    resume_readiness_score: null,
    total_resumes: 0,
    total_analyses: 0,
  });

  const [recentAnalyses, setRecentAnalyses] = useState<RecentResumeAnalysis[]>([]);
  const [recentInterviews, setRecentInterviews] = useState<RecentInterviewSession[]>([]);

  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      try {
        // Get current user
        const { data: { user} } = await supabase.auth.getUser();
        if (!user) {
          setRecentAnalyses([]);
          setRecentInterviews([]);
          setIsLoading(false);
          return;
        }

        // Fetch dashboard metrics from API
        const [metricsResp, analysesResp, interviewsResp] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/dashboard/metrics`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${user.access_token}`,
            },
          }),
          fetch(`${API_BASE_URL}/api/v1/resumes/`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${user.access_token}`,
            },
          }),
          fetch(`${API_BASE_URL}/api/v1/interviews/`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${user.access_token}`,
            },
          }),
        ]);

        if (!metricsResp.ok) throw new Error("Failed to load metrics");
        if (!analysesResp.ok) throw new Error("Failed to load resume analyses");
        if (!interviewsResp.ok) throw new Error("Failed to load interview sessions");

        const metricsData = await metricsResp.json();
        const analysesData = await analysesResp.json();
        const interviewsData = await interviewsResp.json();

        setMetrics({
          total_interviews: metricsData.total_interviews || 0,
          completed_interviews: metricsData.completed_interviews || 0,
          average_score: metricsData.average_score || 0,
          resume_readiness_score: metricsData.resume_readiness_score || null,
          total_resumes: metricsData.total_resumes || 0,
          total_analyses: metricsData.total_analyses || 0,
        });

        // Transform recent resume analyses
        setRecentAnalyses(
          (analysesData as any[] || [])
            .slice(0, 5)
            .map((a: any) => ({
              id: a.id,
              overall_score: a.overall_score,
              created_at: a.created_at,
            }))
        );

        // Transform recent interview sessions
        setRecentInterviews(
          (interviewsData as any[] || [])
            .slice(0, 5)
            .map((s: any) => ({
              id: s.id,
              interview_type: s.interview_type,
              target_role: s.target_role,
              status: s.status,
              overall_score: s.overall_score,
              created_at: s.created_at,
            }))
        );
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
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
          <Loader2 className="h-8 w-8 animate-spin mr-3" /> Loading dashboard...
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
                <p className="text-3xl font-bold text-fg-primary">
                  {metrics.resume_readiness_score || 0}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Resume Analyses */}
        <div className="card p-6 border border-border">
          <h2 className="font-medium text-fg-primary mb-4">Recent Resume Analyses</h2>
          {recentAnalyses.length === 0 && (
            <p className="text-fg-secondary text-sm">
              No resume analyses yet. Upload and analyze a resume to see your readiness score.
            </p>
          )}

          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentAnalyses.map((analysis) => (
              <div key={analysis.id} className="flex items-center justify-between p-3 rounded-md transition-colors hover:bg-muted">
                <span className="text-fg-secondary text-sm">{analysis.created_at}</span>
                <span className="font-medium text-accent-primary">
                  {analysis.overall_score || 0}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Interview Sessions */}
        <div className="card p-6 border border-border">
          <h2 className="font-medium text-fg-primary mb-4">Recent Interview Sessions</h2>
          {recentInterviews.length === 0 && (
            <p className="text-fg-muted text-sm">
              No interview sessions yet. Start a mock interview to get started.
            </p>
          )}

          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentInterviews.map((session) => (
              <div key={session.id} className="flex items-center justify-between p-3 rounded-md transition-colors hover:bg-muted">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-fg-secondary" />
                  <span className="text-fg-secondary text-sm">
                    {session.interview_type}
                  </span>
                  <span className="ml-2 text-fg-secondary text-sm">
                    {session.target_role || "Unknown Role"}
                  </span>
                </div>
                <span className="text-accent-primary font-medium">
                  {session.overall_score || 0}/10
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;