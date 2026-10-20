import { Link, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ResumeAnalyzerPage from "./pages/ResumeAnalyzerPage";
import JobAnalyzerPage from "./pages/JobAnalyzerPage";
import MockInterviewsPage from "./pages/MockInterviewsPage";
import TechnicalPracticePage from "./pages/TechnicalPracticePage";
import CodingPracticePage from "./pages/CodingPracticePage";
import InterviewHistoryPage from "./pages/InterviewHistoryPage";
import SettingsPage from "./pages/SettingsPage";
import LandingPage from "./pages/LandingPage";

function AccountPage() {
  const { user, signOut, session } = useAuth();

  return (
    <main>
      <h1>Dashboard</h1>
      <p>Signed in as {user?.email}</p>
      <button onClick={() => void signOut()}>Log out</button>
    </main>
  );
}

function HomePage() {
  return (
    <main>
      <h1>Welcome to PrepPilot AI</h1>
      <Link to="/app">Go to Dashboard</Link>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<DashboardPage />} />
      <Route path="/profile" element={<SettingsPage />} />
      <Route path="/resume-analyzer" element={<ResumeAnalyzerPage />} />
      <Route path="/job-analyzer" element={<JobAnalyzerPage />} />
      <Route path="/mock-interviews" element={<MockInterviewsPage />} />
      <Route path="/technical-practice" element={<TechnicalPracticePage />} />
      <Route path="/coding-practice" element={<CodingPracticePage />} />
      <Route path="/interview-history" element={<InterviewHistoryPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  );
}