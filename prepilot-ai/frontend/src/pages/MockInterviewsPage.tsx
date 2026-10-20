import React, { useState } from "react";
import { Loader2, Microscope, MessageCircle, LogOut, Calendar, MenuSquare, Shield, Settings, TrendingUp } from "lucide-react";
import { supabase } from "../lib/supabase";

interface InterviewSession {
  id: number;
  interview_type: string;
  target_role: string | null;
  difficulty: string;
  status: string;
  total_questions: number | null;
  overall_score: number | null;
  created_at: string;
}

interface InterviewQuestion {
  id: number;
  question_text: string;
  question_type: string;
  expected_topics: string[];
  question_order: number;
}

interface CurrentSessionState {
  id: number;
  questions: InterviewQuestion[];
  currentQuestionIndex: number;
  answers: string[];
}

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

const MockInterviewsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interviewTypes] = useState(["technical", "behavioral", "mixed"]);
  const [selectedType, setSelectedType] = useState("technical");
  const [targetRole, setTargetRole] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("junior");
  const [difficulty, setDifficulty] = useState("medium");
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [currentSession, setCurrentSession] = useState<CurrentSessionState | null>(
    null
  );

  const startInterview = async () => {
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

      // Call backend API to create interview session
      const response = await fetch(`${API_BASE_URL}/api/v1/interviews/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          interview_type: selectedType,
          target_role: targetRole || undefined,
          difficulty: difficulty,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start interview");
      }

      const session: InterviewSession = await response.json;
      setSessions((prev) => [session, ...prev].slice(0, 5));

      // Generate initial questions
      await generateQuestions(session.id);

      setCurrentSession({
        id: session.id,
        questions: [],
        currentQuestionIndex: 0,
        answers: [],
      });
    } catch (err: any) {
      console.error("Start interview error:", err);
      setError(err.message || "Failed to start interview");
    } finally {
      setIsLoading(false);
    }
  };

  const generateQuestions = async (sessionId: number) => {
    setIsLoading(true);
    setError(null);

    try {
      // Get current user
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) return;

      // Call backend API for Gemini question generation
      const response = await fetch(`${API_BASE_URL}/api/v1/interviews/${sessionId}/questions`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate questions");
      }

      const questions: InterviewQuestion[] = await response.json;
      setCurrentSession((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          questions,
          currentQuestionIndex: 0,
          answers: new Array(questions.length).fill(""),
        };
      });
    } catch (err: any) {
      console.error("Generate questions error:", err);
      setError(err.message || "Failed to generate questions");
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async (questionId: number, answerText: string) => {
    if (!currentSession) return;

    setIsLoading(true);
    setError(null);

    try {
      // Get current user
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) return;

      // Call backend API for answer evaluation
      const response = await fetch(`${API_BASE_URL}/api/v1/interviews/${currentSession.id}/answers`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question_id: questionId,
          answer_text: answerText,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to submit answer");
      }

      const answer = await response.json;

      // Update current session answers
      setCurrentSession((prev) => {
        if (!prev) return null;
        const newAnswers = [...prev.answers];
        newAnswers[prev.currentQuestionIndex] = answerText;
        return {
          ...prev,
          answers: newAnswers,
          currentQuestionIndex: prev.currentQuestionIndex + 1,
        };
      });
    } catch (err: any) {
      console.error("Submit answer error:", err);
      setError(err.message || "Failed to submit answer");
    } finally {
      setIsLoading(false);
    }
  };

  const finishInterview = async () => {
    if (!currentSession) return;

    setIsLoading(true);
    setError(null);

    try {
      // Get current user
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) return;

      // Call backend API to complete interview
      const response = await fetch(`${API_BASE_URL}/api/v1/interviews/${currentSession.id}/complete`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to complete interview");
      }

      const session = await response.json;
      setSessions((prev) => [session, ...prev].slice(0, 5));
      setCurrentSession(null);
    } catch (err: any) {
      console.error("Finish interview error:", err);
      setError(err.message || "Failed to complete interview");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load recent sessions on mount
    const loadSessions = async () => {
      try {
        const { data: { user} } = await supabase.auth.getUser();
        if (!user) return;

        const response = await fetch(`${API_BASE_URL}/api/v1/interviews/`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${user.access_token}`,
          },
        });

        if (!response.ok) return;

        const data: InterviewSession[] = await response.json();
        setSessions(data.slice(0, 5));
      } catch (err) {
        console.error("Load sessions error:", err);
      }
    };

    loadSessions();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-fg-muted">
          <Loader2 className="h-8 w-8 animate-spin mr-3" /> Loading...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-6">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">
          Mock Interviews
        </h1>

        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">
            Start New Interview
          </h2>

          <form className="space-y-4">
            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Interview Type
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
              >
                <option value="technical">Technical</option>
                <option value="behavioral">Behavioral</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>

            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Target Role
              </label>
              <input
                placeholder="e.g., Software Engineer"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="input w-full"
                aria-label="Target role"
              />
            </div>

            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Experience Level
              </label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
              >
                <option value="junior">Junior (0-2 years)</option>
                <option value="mid">Mid (2-5 years)</option>
                <option value="senior">Senior (5+ years)</option>
              </select>
            </div>

            <div>
              <label className="block text-fg-secondary text-sm mb-2">
                Difficulty
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="select w-full rounded border border-border p-2 focus:outline-none focus:border-accent-primary"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <button
              onClick={startInterview}
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
              {isLoading ? "Starting..." : "Generate Questions"}
            </button>
          </form>
        </div>

        {currentSession && currentSession.questions && currentSession.questions.length > 0 && (
          <div className="card p-6 border border-border mb-6">
            <h2 className="text-font-medium text-fg-primary mb-4">
              Interview Question
            </h2>

            <p className="text-fg-secondary text-sm mb-4">
              {currentSession.questions[currentSession.currentQuestionIndex].question_text}
            </p>

            <textarea
              rows={4}
              placeholder="Write your answer here..."
              value={currentSession.answers[currentSession.currentQuestionIndex] || ""}
              onChange={(e) =>
                setCurrentSession((prev) => {
                  if (!prev) return null;
                  const newAnswers = [...prev.answers];
                  newAnswers[prev.currentQuestionIndex] = e.target.value;
                  return {
                    ...prev,
                    answers: newAnswers,
                  };
                })
              }
              className="input w-full resize-none p-3 border border-border rounded mb-3"
            ></textarea>

            <button
              onClick={() => submitAnswer(
                currentSession.questions[currentSession.currentQuestionIndex].id,
                currentSession.answers[currentSession.currentQuestionIndex] || ""
              )}
              disabled={isLoading}
              className={`btn btn-primary w-full py-3 text-lg font-medium transition-colors ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isLoading ? "Evaluating..." : "Submit Answer"}
            </button>
          </div>
        )}

        <div>
          <h2 className="text-font-medium text-fg-primary mb-4">
            Recent Sessions
          </h2>

          {sessions.length === 0 && (
            <p className="text-fg-secondary text-sm">
              No recent sessions yet. Start a new mock interview above.
            </p>
          )}

          <div className="space-y-3 max-h-80 overflow-y-auto">
            {sessions.map((session) => (
              <div key={session.id} className="p-3 rounded-md border border-border hover:bg-muted transition-colors">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-fg-secondary" />
                  <div>
                    <span className="font-medium text-fg-primary">
                      {session.interview_type} interview
                    </span>
                    <span className="text-fg-secondary text-sm">
                      {session.target_role || "Unknown Role"}
                    </span>
                  </div>
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <span className="text-accent-primary font-medium">
                    {session.overall_score || 0}/10
                  </span>
                  <span className="text-fg-secondary text-sm">({session.created_at})</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MockInterviewsPage;