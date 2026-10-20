import React, { useEffect, useState } from "react";
import { Loader2, Upload, FileText, Folder, LogOut } from "lucide-react";

// Import Supabase from the configured lib file
import { supabase } from "../lib/supabase";

// API base URL from environment - no hardcoded localhost
const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

interface ResumeUploadResponse {
  id: number;
  user_id: string;
  original_filename: string;
  storage_path: string;
  extracted_text: string | null;
  created_at: string;
  updated_at: string;
}

interface ResumeAnalyzerPageProps {
  match?: {
    params: { resumeId?: string };
  };
}

const ResumeAnalyzerPage: React.FC<ResumeAnalyzerPageProps> = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resume, setResume] = useState({
    filename: "",
    extractedText: "",
    analysis: null,
    resumeId: null as number | null,
  });
  const [uploadStatus, setUploadStatus] = useState<{
    status: "idle" | "uploading" | "analyzing" | "success" | "error";
    message: string;
  }>({ status: "idle", message: "" });

  const [recentResumes, setRecentResumes] = useState<
    ResumeUploadResponse[]
  >([]);

  useEffect(() => {
    // Load recent resumes when component mounts
    const loadRecentResumes = async () => {
      try {
        // Use auth.getUser instead of direct table access for secure data access
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          setRecentResumes([]);
          return;
        }

        const { data, error } = await supabase
          .from("resumes")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false })
          .limit(5);

        if (error) throw error;
        setRecentResumes(data || []);
      } catch (err) {
        console.error("Failed to load recent resumes:", err);
        setRecentResumes([]);
      }
    };

    loadRecentResumes();
  }, []);

  const handleFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file type
    const allowedTypes = [".pdf", ".docx"];
    const fileExt = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    if (!allowedTypes.includes(fileExt)) {
      setError(`Invalid file type. Allowed: .pdf, .docx`);
      return;
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setError(`File too large. Maximum size: 10MB`);
      return;
    }

    setIsLoading(true);
    setError(null);
    setUploadStatus({ status: "uploading", message: "Uploading resume..." });

    try {
      // Get current user session for auth token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        setError("No authenticated session. Please sign in first.");
        setIsLoading(false);
        return;
      }

      // Create FormData - let browser generate multipart boundary automatically
      const formData = new FormData();
      formData.append("file", file, file.name);

      // Upload to FastAPI endpoint - NO manual Content-Type for FormData
      const response = await fetch(`${API_BASE_URL}/v1/resumes/upload`, {
        method: "POST",
        headers: {
          // Only include auth token; let browser set content-type boundary
          Authorization: `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const uploadedResume: ResumeUploadResponse = await response.json();
      setResume({
        filename: uploadedResume.original_filename,
        extractedText: uploadedResume.extracted_text || "",
        analysis: null,
        resumeId: uploadedResume.id,
      });

      // Refresh recent resumes list
      const { data } = await supabase
        .from("resumes")
        .select("*")
        .eq("user_id", (await supabase.auth.getUser()).data?.user?.id || "")
        .order("created_at", { ascending: false })
        .limit(5);
      setRecentResumes(data || []);

      setUploadStatus({
        status: "success",
        message: `Resume "${uploadedResume.original_filename}" uploaded successfully!`,
      });

      // Trigger auto-analysis after successful upload
      setIsLoading(true);
      setUploadStatus({ status: "analyzing", message: "Analyzing resume with Gemini AI..." });

      // Call the analyze endpoint with the actual resume ID
      const analyzeResponse = await fetch(
        `${API_BASE_URL}/v1/resumes/${uploadedResume.id}/analyze`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ resume_id: uploadedResume.id }),
        }
      );

      if (!analyzeResponse.ok) {
        const analyzeError = await analyzeResponse.json();
        // Don't fail the whole upload if analysis fails - just show warning
        console.error("Analysis failed:", analyzeError);
        setUploadStatus({
          status: "success",
          message: `Resume uploaded successfully, but analysis failed: ${analyzeError.detail || "Unknown error"}`,
        });
      } else {
        const analysis = await analyzeResponse.json();
        setResume({
          filename: uploadedResume.original_filename,
          extractedText: uploadedResume.extracted_text || "",
          analysis: {
            overall_score: analysis.overall_score,
            strengths: analysis.strengths || [],
            missing_skills: analysis.missing_skills || [],
            improvement_suggestions: analysis.improvement_suggestions || [],
          },
        });
        setUploadStatus({
          status: "success",
          message: "Resume uploaded and analyzed successfully!",
        });
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(err.message || "Upload failed");
      setUploadStatus({
        status: "error",
        message: err.message || "Upload failed",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!resume.extractedText?.trim()) {
      setError("No text extracted from resume. Please upload a valid PDF or DOCX file.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setUploadStatus({ status: "analyzing", message: "Analyzing resume with Gemini AI..." });

    try {
      const { data: { session} } = await supabase.auth.getSession();
      if (!session) {
        setError("No authenticated session. Please sign in first.");
        setIsLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/v1/resumes/analyze`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ resume_id: resume.resumeId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Analysis failed");
      }

      const analysis = await response.json();
      setResume({
        filename: resume.filename,
        extractedText: resume.extractedText,
        analysis: {
          overall_score: analysis.overall_score,
          strengths: analysis.strengths || [],
          missing_skills: analysis.missing_skills || [],
          improvement_suggestions: analysis.improvement_suggestions || [],
        },
      });
      setUploadStatus({
        status: "success",
        message: "Resume analyzed successfully!",
      });
    } catch (err: any) {
      console.error("Analysis error:", err);
      setError(err.message || "Analysis failed");
      setUploadStatus({
        status: "error",
        message: err.message || "Analysis failed",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteResume = async (resumeId: number) => {
    if (!window.confirm("Are you sure you want to delete this resume?")) return;

    try {
      const { data: { session} } = await supabase.auth.getSession();
      if (!session) return;

      const response = await fetch(`${API_BASE_URL}/v1/resumes/${resumeId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Delete failed");
      }

      // Refresh recent resumes
      const { data } = await supabase
        .from("resumes")
        .select("*")
        .eq("user_id", (await supabase.auth.getUser()).data?.user?.id || "")
        .order("created_at", { ascending: false })
        .limit(5);
      setRecentResumes(data || []);

      // If deleting the currently viewed resume, reset state
      if (resume.resumeId === resumeId) {
        setResume({
          filename: "",
          extractedText: "",
          analysis: null,
          resumeId: null,
        });
      }

      setError(null);
    } catch (err: any) {
      console.error("Delete error:", err);
      setError(err.message || "Delete failed");
    }
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">
          Resume Analyzer
        </h1>

        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">
            Upload Resume
          </h2>

          <div className="flex flex-col gap-4">
            <label className="flex items-center gap-2 cursor-pointer text-fg-secondary hover:text-accent-primary transition-colors">
              <input
                type="file"
                accept=".pdf, .docx"
                onChange={handleFileChange}
                className="hidden"
              />
              <div>
                <Icon className="h-5 w-5 text-fg-muted" />
                <span>Select PDF or DOCX file</span>
              </div>
            </label>

            <button
              onClick={() => document.querySelector('input[type="file"]')?.click()}
              className="btn btn-secondary flex items-center gap-2"
            >
              <Icon className="h-4 w-4" />
              Browse
            </button>

            {resume.filename && (
              <div className="p-3 bg-bg-secondary rounded-md mb-4">
                <span className="font-medium text-fg-primary">
                  {resume.filename}
                </span>
              </div>
            )}

            {/* Upload Status */}
            {uploadStatus.status !== "idle" && (
              <div className="p-3 bg-bg-secondary rounded-md mb-4">
                <span className="text-fg-secondary text-sm">
                  {uploadStatus.message}
                </span>
              </div>
            )}

            {/* Upload Progress */}
            {uploadStatus.status === "uploading" && (
              <div className="p-3 bg-bg-secondary rounded-md mb-4">
                <span className="text-fg-secondary text-sm">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Uploading...
                </span>
              </div>
            )}

            {uploadStatus.status === "analyzing" && (
              <div className="p-3 bg-bg-secondary rounded-md mb-4">
                <span className="text-fg-secondary text-sm">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Analyzing with Gemini AI...
                </span>
              </div>
            )}

            {resume.analysis && (
              <div className="p-4 bg-bg-secondary rounded-md mb-6">
                <h3 className="font-medium text-fg-primary mb-2">
                  Analysis Results
                </h3>
                <p className="text-fg-secondary text-sm">
                  Overall Score: {resume.analysis.overall_score || 0}%
                </p>
                <ul className="list-disc list-inside space-y-1 text-fg-secondary text-sm">
                  <li>
                    Strengths: {" "}
                    {resume.analysis.strengths?.join(", ") || "None identified"}
                  </li>
                  <li>
                    Missing Skills: {" "}
                    {resume.analysis.missing_skills?.join(", ") || "None identified"}
                  </li>
                  <li>
                    Improvement Suggestions: {" "}
                    {resume.analysis.improvement_suggestions?.join(", ") || "None provided"}
                  </li>
                </ul>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="mt-4 flex gap-3">
            {resume.filename && !resume.analysis && (
              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {isLoading ? "Analyzing..." : "Analyze Resume"}
              </button>
            )}

            {resume.filename && resume.analysis && (
              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="btn btn-outline w-full py-3 text-lg font-medium transition-colors"
              >
                Re-analyze Resume
              </button>
            )}

            {recentResumes.length > 0 && (
              <button
                onClick={() => window.location.href = "/dashboard"}
                className="btn btn-outline w-full py-3 text-lg font-medium transition-colors"
              >
                View Dashboard
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeAnalyzerPage;