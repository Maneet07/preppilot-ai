import React, { useState } from "react";
import { Loader2, Microscope, LightBulb, Loader2 as Loader2Icon, Flag, TrendingUp } from "lucide-react";
import { supabase } from "../lib/supabase";

interface PracticeQuestion {
  id: number;
  topic: string;
  difficulty: string;
  question_text: string;
  question_data: Record<string, any>;
  created_at: string;
}

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

const TechnicalPracticePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topics] = useState([
    "data structures",
    "algorithms",
    "dbms",
    "operating systems",
    "networks",
    "oop",
    "web development",
    "python",
    "java",
    "software engineering",
    "cloud computing",
    "ai/ml fundamentals",
  ]);
  const [selectedTopic, setSelectedTopic] = useState(topics[0]);
  const [difficultyOptions] = useState(["junior", "mid", "senior"]);
  const [selectedDifficulty, setSelectedDifficulty] = useState("junior");
  const [question, setQuestion] = useState<PracticeQuestion | null>(null);

  const generateQuestion = async () => {
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

      // Call backend API for Gemini question generation
      const response = await fetch(`${API_BASE_URL}/api/v1/practice/questions/generate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: selectedTopic,
          difficulty: selectedDifficulty,
          language: "Python",
          experience_level: "junior",
          focus_areas: [],
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate question");
      }

      const generated = await response.json();
      setQuestion({
        id: generated.id || Date.now(),
        topic: selectedTopic,
        difficulty: selectedDifficulty,
        question_text: generated.question_text || "Generating question...",
        question_data: generated.question_data || {},
        created_at: new Date().toISOString(),
      });
    } catch (err: any) {
      console.error("Question generation error:", err);
      setError(err.message || "Failed to generate question");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswer = async (answerText: string) => {
    if (!question) return;

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

      // Call backend API for answer evaluation
      const response = await fetch(`${API_BASE_URL}/api/v1/practice/attempts`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          practice_question_id: question.id,
          answer_text: answerText,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to evaluate answer");
      }

      const result = await response.json();
      // Could show the result to user
      console.log("Practice attempt result:", result);
    } catch (err: any) {
      console.error("Practice attempt error:", err);
      setError(err.message || "Failed to evaluate answer");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">
          Technical Practice
        </h1>

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">
            Generate Practice Question
          </h2>

          <form className="space-y-4">
            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Topic
              </label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
              >
                {topics.map((topic) => (
                  <option key={topic} value={topic}>
                    {topic}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Difficulty
              </label>
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
              >
                <option value="junior">Junior</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
              </select>
            </div>

            <button
              onClick={generateQuestion}
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isLoading ? "Generating..." : "Generate Question"}
            </button>
          </form>
        </div>

        {question && (
          <div className="card p-6 border border-border mb-6">
            <h2 className="text-font-medium text-fg-primary mb-4">
              Practice Question
            </h2>

            <p className="text-fg-secondary text-sm mb-4">
              {question.question_text}
            </p>

            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Your Answer
              </label>
              <textarea
                rows={4}
                placeholder="Write your answer here..."
                className="input w-full resize-none p-3 border border-border rounded"
                onChange={(e) => {
                  // Could update state, but we'll just submit on button click
                }}
              ></textarea>
            </div>

            <button
              onClick={() => {
                // In a real implementation, we'd call handleAnswer with the answer text
                // For now, just show a message
                alert("Answer submission would evaluate with Gemini AI");
              }}
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isLoading ? "Evaluating..." : "Submit Answer"}
            </button>
          </div>
        )}

        {isLoading && (
          <div className="mt-6 text-center text-fg-muted">
            <Loader2Icon className="h-5 w-5 animate-spin mr-2" />
            Generating question with Gemini AI...
          </div>
        )}
      </div>
    </div>
  );
};

export default TechnicalPracticePage;