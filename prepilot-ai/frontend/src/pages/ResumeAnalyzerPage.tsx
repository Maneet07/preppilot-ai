import React from "react";
import { Loader2, Upload, FileText, Folder, LogOut } from "lucide-react";
import "../index.css";

const ResumeAnalyzerPage: React.FC = () => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [resume, setResume] = React.useState({
    filename: "",
    extractedText: "",
    analysis: null,
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e: any) => {
      const fileContent = e.target?.result;
      setIsLoading(true);
      
      // In real implementation, would send to backend for analysis
      // For now, just store the filename
      setResume({
        filename: file.name,
        extractedText: "",
        analysis: null,
      });
      setIsLoading(false);
    };
    reader.readAsText(file);
  };

  const handleAnalyze = async () => {
    if (!resume.extractedText?.trim()) {
      setError("No text extracted from resume. Please upload a valid PDF or DOCX file.");
      return;
    }
    setIsLoading(true);
    setError(null);
    
    // Would call backend API for Gemini analysis
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Resume Analyzer</h1>
        
        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">Upload Resume</h2>
          
          <div className="flex flex-col gap-4">
            <label className="flex items-center gap-2 cursor-pointer text-fg-secondary hover:text-accent-primary transition-colors">
              <input type="file" accept=".pdf, .docx" onChange={handleFileChange} className="hidden" />
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
                <span className="font-medium text-fg-primary">{resume.filename}</span>
              </div>
            )}
          </div>

          {resume.analysis && (
            <div className="p-4 bg-bg-secondary rounded-md mb-6">
              <h3 className="font-medium text-fg-primary mb-2">Analysis Results</h3>
              <p className="text-fg-secondary text-sm">
                Overall Score: {resume.analysis.overall_score || 0}%
              </p>
              <ul className="list-disc list-inside space-y-1 text-fg-secondary text-sm">
                <li>Strengths: {resume.analysis.strengths?.join(", ") || "None identified"}</li>
                <li>Missing Skills: {resume.analysis.missing_skills?.join(", ") || "None identified"}</li>
                <li>Improvement Suggestions: {resume.analysis.improvement_suggestions?.join(", ") || "None provided"}</li>
              </ul>
            </div>
          )}
        </div>

        <button
          onClick={handleAnalyze}
          disabled={isLoading || !resume.filename}
          className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {isLoading ? "Analyzing..." : "Analyze Resume"}
        </button>

        {isLoading && (
          <div className="mt-4 text-center text-fg-muted">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            Analyzing with Gemini AI...
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeAnalyzerPage;