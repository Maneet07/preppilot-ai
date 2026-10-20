import React, { useState } from "react";
import { Loader2, Microscope, LightBulb, Loader2 as Loader2Icon, Flag, TrendingUp } from "lucide-react";
import "../index.css";

const TechnicalPracticePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topics] = useState(["data structures", "algorithms", "dbms", "operating systems", "networks", "oop", "web development", "python", "java", "software engineering", "cloud computing", "ai/ml fundamentals"]);
  const [selectedTopic, setSelectedTopic] = useState(topics[0]);
  const [difficultyOptions] = useState(["junior", "mid", "senior"]);
  const [selectedDifficulty, setSelectedDifficulty] = useState("junior");
  
  const generateQuestion = async () => {
    setIsLoading(true);
    setError(null);
    
    // Would call backend API for Gemini question generation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Simulate a generated question
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-fg-primary mb-6">Technical Practice</h1>
        
        <div className="card p-6 border border-border mb-6">
          <h2 className="text-font-medium text-fg-primary mb-4">Generate Practice Question</h2>
          
          <form className="space-y-4">
            <div>
              <label className="block text-fg-secondary text-sm mb-2">Topic</label>
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
              <label className="block text-fg-secondary text-sm mb-2">Difficulty</label>
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