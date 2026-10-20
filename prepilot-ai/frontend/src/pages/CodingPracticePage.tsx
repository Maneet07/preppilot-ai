import React, { useState } from "react";
import { Loader2, Code, Loader2 as Loader2Icon, TrendingUp, GitBranch, Terminal, LogOut } from "lucide-react";
import "../index.css";

const CodingPracticePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [languages] = useState(["Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Rust"]);
  const [selectedLanguage, setSelectedLanguage] = useState("Python");
  
  const generateProblem = async () => {
    setIsLoading(true);
    setError(null);
    
    // Would call backend API for Gemini problem generation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Coding Practice</h1>
        
        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">Generate Coding Problem</h2>
          
          <form className="space-y-4">
            <div>
              <label className="block text-fg-secondary text-sm mb-2">Programming Language</label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
              >
                {languages.map((lang) => (
                  <option key={lang} value={lang}>
                    {lang}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={generateProblem}
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isLoading ? "Generating..." : "Generate Problem"}
            </button>
          </form>
        </div>

        {isLoading && (
          <div className="mt-6 text-center text-fg-muted">
            <Loader2Icon className="h-5 w-5 animate-spin mr-2" />
            Generating problem with Gemini AI...
          </div>
        )}
      </div>
    </div>
  );
};

export default CodingPracticePage;