import React, { useState } from "react";
import { Loader2, Code, Loader2 as Loader2Icon, TrendingUp, GitBranch, Terminal, LogOut } from "lucide-react";
import { supabase } from "../lib/supabase";

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

interface CodingSubmission {
  id: number;
  problem_title: string;
  programming_language: string;
  problem_statement: string;
  submitted_code: string;
  review_json: Record<string, any>;
  created_at: string;
}

const CodingPracticePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [languages] = useState(["Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Rust"]);
  const [selectedLanguage, setSelectedLanguage] = useState("Python");
  const [submission, setSubmission] = useState({
    problem_title: "",
    programming_language: "Python",
    problem_statement: "",
    submitted_code: "",
  });

  const generateProblem = async () => {
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

      // Call backend API for Gemini code generation
      const response = await fetch(`${API_BASE_URL}/api/v1/coding/review`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          problem_title: selectedLanguage,
          programming_language: selectedLanguage,
          problem_statement: `Write a function to solve a coding problem in ${selectedLanguage}.`,
          submitted_code: "",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate problem");
      }

      const result = await response.json();
      setSubmission({
        problem_title: result.problem_title || "Coding Problem",
        programming_language: selectedLanguage,
        problem_statement: result.problem_statement || "",
        submitted_code: result.submitted_code || "",
      });
    } catch (err: any) {
      console.error("Code generation error:", err);
      setError(err.message || "Failed to generate coding problem");
    } finally {
      setIsLoading(false);
    }
  };

  const reviewCode = async () => {
    if (!submission.submitted_code?.trim()) {
      setError("Please enter or paste code to review.");
      return;
    }
    setIsLoading(true);
    setError(null);

    try {
      // Get current user
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) {
        setError("No authenticated session.");
        setIsLoading(false);
        return;
      }

      // Call backend API for Gemini code review
      const response = await fetch(`${API_BASE_URL}/api/v1/coding/review`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          problem_title: submission.problem_title,
          programming_language: submission.programming_language,
          problem_statement: submission.problem_statement,
          submitted_code: submission.submitted_code,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Code review failed");
      }

      const review = await response.json();
      // Could display the review results to the user
      console.log("Code review result:", review);
    } catch (err: any) {
      console.error("Code review error:", err);
      setError(err.message || "Code review failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">
          Coding Practice
        </h1>

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">
            Generate Coding Problem
          </h2>

          <form className="space-y-4">
            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Programming Language
              </label>
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

        {submission.problem_statement && (
          <div className="card p-6 border border-border mb-6">
            <h2 className="text-font-medium text-fg-primary mb-4">
              Coding Problem
            </h2>

            <p className="text-fg-secondary text-sm mb-4">
              {submission.problem_statement}
            </p>

            <textarea
              rows={6}
              placeholder="Write your solution here..."
              value={submission.submitted_code}
              onChange={(e) => setSubmission({ ...submission, submitted_code: e.target.value })}
              className="input w-full resize-none p-3 border border-border rounded h-64"
            ></textarea>
          </div>
        )}

        {submission.submitted_code && (
          <div>
            <button
              onClick={reviewCode}
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isLoading ? "Reviewing..." : "Review Code with Gemini AI"}
            </button>
          </div>
        )}

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