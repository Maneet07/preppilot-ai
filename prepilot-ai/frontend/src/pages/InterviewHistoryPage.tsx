import React, { useState } from "react";
import { Loader2, History, Calendar, BarChart2, LogOut, Shield, TrendingUp, MessageCircle } from "lucide-react";
import "../index.css";

const InterviewHistoryPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sessions] = useState([
    {
      id: 1,
      type: "technical",
      role: "Software Engineer",
      difficulty: "hard",
      date: "2024-01-20",
      score: 8.5,
      status: "completed",
    },
    {
      id: 2,
      type: "behavioral",
      role: "Product Manager",
      difficulty: "medium",
      date: "2024-01-18",
      score: 7.2,
      status: "completed",
    },
    {
      id: 3,
      type: "technical",
      role: "Software Engineer",
      difficulty: "hard",
      date: "2024-01-15",
      score: 9.0,
      status: "completed",
    },
  ]);

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Interview History</h1>
        
        {error && (
          <div className="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">Session History</h2>
          
          {sessions.length === 0 && (
            <p className="text-fg-secondary text-sm">No interview sessions yet. Start a mock interview to create your first session.</p>
          )}
          
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {sessions.map((session) => (
              <div key={session.id} className="p-3 rounded-md border border-border hover:bg-muted transition-colors">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-fg-secondary" />
                  <div>
                    <span className="font-medium text-fg-primary">{session.role}</span>
                    <span className="text-fg-secondary text-sm"> {session.type} interview</span>
                  </div>
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <span className="text-accent-primary font-medium">{session.score}/10</span>
                  <span className="text-fg-secondary text-sm">({session.date})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-font-medium text-fg-primary mb-4">Performance Summary</h2>
          <p className="text-fg-secondary text-sm">Track your progress and improve with each session.</p>
        </div>
      </div>
    </div>
  );
};

// Icon component mapping
const getIconClass = (type: string) => {
  switch (type) {
    case 'technical':
      return Microscope;
    case 'behavioral':
      return Shield;
    case 'mixed':
      return Heart;
  }
};

export default InterviewHistoryPage;