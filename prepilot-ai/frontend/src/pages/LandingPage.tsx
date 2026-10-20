import React from "react";
import { Search, Folder, Shield, Heart, FileText, Mail, Phone, Linkedin, GitHub } from "lucide-react";
import "../index.css";

const LandingPage: React.FC = () => {
  return (
    <main className="min-h-screen bg-bg-primary">
      <header className="flex items-center justify-between px-4 py-4 border-b border-border bg-white sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Icon className="h-6 w-6 text-accent-primary" />
          <span className="font-xl font-bold text-fg-primary">PrepPilot AI</span>
        </div>
        <nav>
          <a href="#features" className="text-fg-secondary hover:text-accent-primary transition-colors text-sm">Features</a>
          <a href="#how-it-works" className="text-fg-secondary hover:text-accent-primary transition-colors text-sm">How it Works</a>
          <a href="#benefits" className="text-fg-secondary hover:text-accent-primary transition-colors text-sm">Benefits</a>
        </nav>
      </header>

      <section className="py-12 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-fg-primary mb-4">
            AI-Powered Interview Preparation
          </h1>
          <p className="text-fg-secondary text-lg mb-8 max-w-2xl mx-auto">
            Comprehensive platform for resume analysis, job matching, and interview practice 
            powered by Google Gemini AI.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="/signup" 
              className="btn btn-primary px-6 py-3 text-lg font-medium"
            >
              Get Started
            </a>
            <a 
              href="/features" 
              className="btn btn-secondary px-6 py-3 text-lg font-medium"
            >
              Explore Features
            </a>
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-bg-secondary">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-fg-primary mb-8 text-center">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <div className="card p-6 border border-border">
              <div className="flex items-start gap-3">
                <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium text-fg-primary mb-1">Resume Analysis</h3>
                  <p className="text-fg-secondary text-sm">Upload PDF/DOCX, extract text, get AI-powered analysis with readiness score</p>
                </div>
              </div>
            </div>

            <div className="card p-6 border border-border">
              <div className="flex items-start gap-3">
                <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium text-fg-primary mb-1">Job Analysis</h3>
                  <p className="text-fg-secondary text-sm">Analyze job descriptions, extract required skills, get matching recommendations</p>
                </div>
              </div>
            </div>

            <div className="card p-6 border border-border">
              <div className="flex items-start gap-3">
                <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium text-fg-primary mb-1">Mock Interviews</h3>
                  <p className="text-fg-secondary text-sm">Generate questions with Gemini, evaluate answers, get detailed reports</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-fg-primary mb-8 text-center">How It Works</h2>
          <ol className="list-decimal list-inside max-w-2xl mx-auto space-y-4">
            <li>
              <div className="flex items-start gap-3">
                <span className="text-2xl font-bold text-accent-primary">1</span>
                <div>
                  <p className="font-medium text-fg-primary">Upload Your Resume</p>
                  <p className="text-fg-secondary text-sm">Drag and drop or browse PDF/DOCX files</p>
                </div>
              </div>
            </li>
            <li>
              <div className="flex items-start gap-3">
                <span className="text-2xl font-bold text-accent-primary">2</span>
                <div>
                  <p className="font-medium text-fg-primary">AI Analysis</p>
                  <p className="text-fg-secondary text-sm">Gemini extracts text and analyzes structure, skills, and suggestions</p>
                </div>
              </div>
            </li>
            <li>
              <div className="flex items-start gap-3">
                <span className="text-2xl font-bold text-accent-primary">3</span>
                <div>
                  <p className="font-medium text-fg-primary">Prepare & Practice</p>
                  <p className="text-fg-secondary text-sm">Get mock interviews, technical practice, and coding reviews</p>
                </div>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <section className="py-16 px-4 bg-bg-secondary">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-fg-primary mb-8 text-center">Benefits</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <div className="card p-6 border border-border">
              <div className="flex items-start gap-3">
                <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium text-fg-primary mb-1">Personalized Feedback</h3>
                  <p className="text-fg-secondary text-sm">AI-generated, actionable feedback tailored to your profile</p>
                </div>
              </div>
            </div>

            <div className="card p-6 border border-border">
              <div className="flex items-start gap-3">
                <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium text-fg-primary mb-1">Track Progress</h3>
                  <p className="text-fg-secondary text-sm">Monitor your interview history, scores, and improvements over time</p>
                </div>
              </div>
            </div>

            <div className="card p-6 border border-border">
              <div className="flex items-start gap-3">
                <Icon className="h-6 w-6 text-accent-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium text-fg-primary mb-1">AI-Powered Insights</h3>
                  <p className="text-fg-secondary text-sm">Leverage Google Gemini for intelligent analysis and suggestions</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      <footer className="py-8 px-4 border-t border-border bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-fg-secondary text-sm">
            <span>2024 PrepPilot AI</span>
            <div className="flex gap-4">
              <a href="#" className="hover:text-accent-primary transition-colors">Privacy</a>
              <a href="#" className="hover:text-accent-primary transition-colors">Terms</a>
              <a href="#" className="hover:text-accent-primary transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
};

export default LandingPage;