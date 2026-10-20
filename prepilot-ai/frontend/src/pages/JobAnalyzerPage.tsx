import React, { useState } from "react";
import { Loader2, FileText, Search, Text, Layout, CheckCircle, X, Clock } from "lucide-react";
import "../index.css";

const JobAnalyzerPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState({
    title: "",
    company: "",
    description: "",
    analysis: null,
  });

  const handleAnalyze = async () => {
    if (!job.description?.trim()) {
      setError("Please enter a job description.");
      return;
    }
    setIsLoading(true);
    setError(null);
    
    // Would call backend API for Gemini analysis
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Job Description Analyzer</h1>
        
        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={(e) => e.preventDefault()} className="space-y-4 mb-6">
          <div>
            <label className="block text-fg-secondary text-sm mb-2">Job Title (optional)</label>
            <input
              placeholder="e.g., Software Engineer"
              value={job.title}
              onChange={(e) => setJob({ ...job, title: e.target.value })}
              className="input w-full"
              aria-label="Job title"
            />
          </div>
          
          <div>
            <label className="block text-fg-secondary text-sm mb-2">Company Name (optional)</label>
            <input
              placeholder="e.g., Tech Corp"
              value={job.company}
              onChange={(e) => setJob({ ...job, company: e.target.value })}
              className="input w-full"
              aria-label="Company name"
            />
          </div>
          
          <div>
            <label className="block text-fg-secondary text-sm mb-2">Job Description</label>
            <textarea
              rows={5}
              placeholder="Paste the job description here..."
              value={job.description}
              onChange={(e) => setJob({ ...job, description: e.target.value })}
              className="input w-full resize-none"
              aria-label="Job description"
            ></textarea>
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {isLoading ? "Analyzing..." : "Analyze Job Description"}
          </button>
        </form>

        {job.analysis && (
          <div className="card p-6 border border-border mb-6">
            <h2 className="text-font-medium text-fg-primary mb-4">Analysis Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-fg-secondary text-sm">Required Skills</p>
                <p className="text-fg-primary font-medium mt-1">{job.analysis.required_skills?.join(", ") || "N/A"}</p>
              </div>
              <div>
                <p className="text-fg-secondary text-sm">Preferred Skills</p>
                <p className="text-fg-primary font-medium mt-1">{job.analysis.preferred_skills?.join(", ") || "N/A"}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-fg-secondary text-sm">Matched Skills</p>
                <p className="text-fg-primary font-medium mt-1">{job.analysis.matched_skills?.join(", ") || "N/A"}</p>
              </div>
              <div>
                <p className="text-fg-secondary text-sm">Missing Skills</p>
                <p className="text-fg-primary font-medium mt-1">{job.analysis.missing_skills?.join(", ") || "N/A"}</p>
              </div>
            </div>
            
            {job.analysis.recommendations?.length && (
              <div className="mt-4">
                <p className="text-fg-secondary text-sm">Recommendations</p>
                <ul className="list-disc list-inside space-y-1 text-fg-secondary text-sm">
                  {job.analysis.recommendations.map((rec: string, i: number) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {isLoading && (
          <div className="mt-6 text-center text-fg-muted">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            Analyzing with Gemini AI...
          </div>
        )}
      </div>
    </div>
  );
};

export default JobAnalyzerPage;