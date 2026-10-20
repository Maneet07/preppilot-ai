import React, { useState, useEffect } from "react";
import { Loader2, History, Calendar, BarChart2, LogOut, Shield, TrendingUp, MessageCircle } from "lucide-react";
import { supabase } from "../lib/supabase";

interface InterviewAnswerWithEval {
  id: number;
  session_id: number;
  question_id: number;
  user_id: string;
  answer_text: string | null;
  relevance_score: number | null;
  technical_accuracy_score: number | null;
  communication_score: number | null;
  completeness_score: number | null;
  feedback: string | null;
  suggested_answer: string | null;
  created_at: string;
}

interface InterviewSessionSummary {
  id: number;
  interview_type: string;
  target_role: string | null;
  difficulty: string | null;
  date: string;
  score: number | null;
  status: string;
}

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

const InterviewHistoryPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<InterviewSessionSummary[]>([]);
  const [answers, setAnswers] = useState<InterviewAnswerWithEval[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);

  useEffect(() => {
    const loadInterviewHistory = async () => {
      setIsLoading(true);
      try {
        const { data: { user} } = await supabase.auth.getUser();
        if (!user) {
          setSessions([]);
          setAnswers([]);
          setIsLoading(false);
          return;
        }

        // Fetch all interview sessions
        const sessionsResponse = await fetch(`${API_BASE_URL}/api/v1/interviews/`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${user.access_token}`,
          },
        });

        if (!sessionsResponse.ok) throw new Error("Failed to load sessions");

        const sessionsData: InterviewSessionSummary[] = await sessionsResponse.json();
        setSessions(sessionsData);

        // If we have sessions, fetch answers for the first one
        if (sessionsData.length > 0) {
          setSelectedSessionId(sessionsData[0].id);
          const answersResponse = await fetch(
            `${API_BASE_URL}/api/v1/interviews/${sessionsData[0].id}/answers`,
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${user.access_token}`,
              },
            }
          );

          if (answersResponse.ok) {
            const answersData: InterviewAnswerWithEval[] =
              await answersResponse.json();
            setAnswers(answersData);
          }
        }
      } catch (err: any) {
        console.error("Failed to load interview history:", err);
        setError(err.message || "Failed to load interview history");
      } finally {
        setIsLoading(false);
      }
    };

    loadInterviewHistory();
  }, []);

  const loadSessionAnswers = async (sessionId: number) => {
    setIsLoading(true);
    try {
      const { data: { user} } = await supabase.auth.getUser();
      if (!user) return;

      const answersResponse = await fetch(
        `${API_BASE_URL}/api/v1/interviews/${sessionId}/answers`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${user.access_token}`,
          },
        }
      );

      if (answersResponse.ok) {
        const answersData: InterviewAnswerWithEval[] =
          await answersResponse.json();
        setAnswers(answersData);
        setSelectedSessionId(sessionId);
      }
    } catch (err: any) {
      console.error("Failed to load session answers:", err);
    } finally {
      setIsLoading(false);
    }
  };

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

  // Calculate average score separately to avoid template string parsing issues
  const calculateAverageScore = (answers: InterviewAnswerWithEval[]) => {
    if (answers.length === 0) return 0;
    const totalScore =
      answers.reduce(
        (sum, a) =>
          sum +
          (a.relevance_score || 0) +
          (a.technical_accuracy_score || 0) +
          (a.communication_score || 0) +
          (a.completeness_score || 0),
        0,
      ) / (answers.length * 4);
    return parseFloat(totalScore.toFixed(1));
  };

  const averageScore = calculateAverageScore(answers);

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">
          Interview History
        </h1>

        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">
            Session History
          </h2>

          {sessions.length === 0 && (
            <p className="text-fg-secondary text-sm">
              No interview sessions yet. Start a mock interview to create your first session.
            </p>
          )}

          <div className="space-y-3 max-h-80 overflow-y-auto">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => loadSessionAnswers(session.id)}
                className={`p-3 rounded-md border border-transition ${selectedSessionId === session.id ? "bg-muted border-primary" : "border-border hover:bg-muted transition-colors"}`}
              >
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
                    {session.score || 0}/10
                  </span>
                  <span className="text-fg-secondary text-sm">({session.date})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {selectedSessionId && answers.length > 0 && (
          <div className="card p-6 border border-border mb-6">
            <h2 className="text-font-medium text-fg-primary mb-4">
              Performance Summary
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-fg-secondary text-sm">Total Answers</p>
                <p className="text-3xl font-bold text-fg-primary">{answers.length}</p>
              </div>
              <div>
                <p className="text-fg-secondary text-sm">Average Score</p>
                <p className="text-3xl font-bold text-fg-primary">{averageScore}</p>
              </div>
            </div>

            <div className="space-y-3">
              {answers.map((answer) => (
                <div key={answer.id} className="p-3 rounded-md border border-border hover:bg-muted transition-colors">
                  <p className="text-fg-secondary text-sm">
                    <strong>Q:</strong> {answer.answer_text || "No answer"}
                  </p>
                  <p className="text-fg-secondary text-sm">
                    <strong>A:</strong> {answer.answer_text || "No answer provided"}
                  </p>
                  <p className="text-fg-muted text-xs">
                    {answer.feedback || "No feedback provided"}
                  </p>
                  <p className="text-fg-secondary text-sm">
                    <strong>Scores:</strong> Relevance={answer.relevance_score ||
                      0}, Technical={answer.technical_accuracy_score || 0},
                    Communication={answer.communication_score || 0},
                    Completeness={answer.completeness_score || 0}
                  </p>
                  {answer.suggested_answer && (
                    <p className="text-fg-muted text-sm mt-1">
                      <strong>Suggested Answer:</strong> {answer.suggested_answer}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedSessionId && answers.length === 0 && (
          <div className="bg-bg-secondary p-4 rounded-md mb-6">
            <p className="text-fg-secondary text-sm">
              No answers yet for this session. Start a mock interview to answer questions.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewHistoryPage;