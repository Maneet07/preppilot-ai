-- ============================================================
-- Initial Schema + RLS Policies Migration for PrepPilot AI
-- Creates all tables and enables Row Level Security
-- Ensures users can only access their own private records
-- ============================================================

-- ============================================================
-- Create all tables (idempotent - safe to rerun)
-- ============================================================

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name STRING,
    email STRING UNIQUE NOT NULL,
    target_role STRING,
    experience_level STRING,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    original_filename STRING NOT NULL,
    storage_path STRING NOT NULL,
    extracted_text TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create resume_analyses table
CREATE TABLE IF NOT EXISTS resume_analyses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    overall_score INTEGER,
    strengths JSONB DEFAULT '[]'::jsonb,
    weaknesses JSONB DEFAULT '[]'::jsonb,
    identified_skills JSONB DEFAULT '[]'::jsonb,
    missing_skills JSONB DEFAULT '[]'::jsonb,
    improvement_suggestions JSONB DEFAULT '[]'::jsonb,
    analysis_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create job_analyses table
CREATE TABLE IF NOT EXISTS job_analyses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    job_title STRING,
    company_name STRING,
    job_description TEXT NOT NULL,
    required_skills JSONB DEFAULT '[]'::jsonb,
    preferred_skills JSONB DEFAULT '[]'::jsonb,
    matched_skills JSONB DEFAULT '[]'::jsonb,
    missing_skills JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    analysis_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create job_matches table
CREATE TABLE IF NOT EXISTS job_matches (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    job_analysis_id INTEGER REFERENCES job_analyses(id) ON DELETE SET NULL,
    compatibility_score INTEGER,
    matched_skills JSONB DEFAULT '[]'::jsonb,
    missing_skills JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    match_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create interview_sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    interview_type STRING NOT NULL,
    target_role STRING,
    experience_level STRING,
    difficulty STRING,
    status STRING DEFAULT 'pending' NOT NULL,
    total_questions INTEGER,
    overall_score INTEGER,
    summary TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create interview_questions table
CREATE TABLE IF NOT EXISTS interview_questions (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type STRING,
    expected_topics JSONB DEFAULT '{}'::jsonb,
    question_order INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create interview_answers table
CREATE TABLE IF NOT EXISTS interview_answers (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    answer_text TEXT,
    relevance_score INTEGER,
    technical_accuracy_score INTEGER,
    communication_score INTEGER,
    completeness_score INTEGER,
    feedback TEXT,
    suggested_answer TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create practice_questions table
CREATE TABLE IF NOT EXISTS practice_questions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    topic STRING NOT NULL,
    difficulty STRING,
    question_text TEXT NOT NULL,
    question_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create practice_attempts table
CREATE TABLE IF NOT EXISTS practice_attempts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    practice_question_id INTEGER NOT NULL REFERENCES practice_questions(id) ON DELETE CASCADE,
    answer_text TEXT,
    feedback TEXT,
    score INTEGER,
    completed_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create coding_submissions table
CREATE TABLE IF NOT EXISTS coding_submissions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    problem_title STRING NOT NULL,
    programming_language STRING NOT NULL,
    problem_statement TEXT NOT NULL,
    submitted_code TEXT NOT NULL,
    review_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- ============================================================
-- Enable Row Level Security on all tables
-- ============================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE coding_submissions ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- Profiles table policies
-- ============================================================
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- ============================================================
-- Resumes table policies
-- ============================================================
CREATE POLICY "Users can view own resumes" ON resumes
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own resume" ON resumes
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY "Users can update own resume" ON resumes
    FOR UPDATE USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can delete own resume" ON resumes
    FOR DELETE USING (user_id::text = auth.uid()::text);

-- ============================================================
-- Resume analyses table policies
-- ============================================================
CREATE POLICY "Users can view own resume analyses" ON resume_analyses
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can view analyses by resume" ON resume_analyses
    FOR SELECT USING (resume_id IN (
        SELECT id FROM resumes WHERE user_id::text = auth.uid()::text
    ));
CREATE POLICY "Users can insert own analysis" ON resume_analyses
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);

-- ============================================================
-- Job analyses table policies
-- ============================================================
CREATE POLICY "Users can view own job analyses" ON job_analyses
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own job analysis" ON job_analyses
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY "Users can update own job analysis" ON job_analyses
    FOR UPDATE USING (user_id::text = auth.uid()::text);

-- ============================================================
-- Job matches table policies
-- ============================================================
CREATE POLICY "Users can view own job matches" ON job_matches
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own job match" ON job_matches
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY "Users can update own job match" ON job_matches
    FOR UPDATE USING (user_id::text = auth.uid()::text);

-- ============================================================
-- Interview sessions table policies
-- ============================================================
CREATE POLICY "Users can view own interview sessions" ON interview_sessions
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own interview session" ON interview_sessions
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY "Users can update own interview session" ON interview_sessions
    FOR UPDATE USING (user_id::text = auth.uid()::text);

-- ============================================================
-- Interview questions table policies
-- ============================================================
CREATE POLICY "Users can view own interview questions" ON interview_questions
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM interview_sessions WHERE user_id::text = auth.uid()::text
        )
    );

-- ============================================================
-- Interview answers table policies
-- ============================================================
CREATE POLICY "Users can view own interview answers" ON interview_answers
    FOR SELECT USING (
        question_id IN (
            SELECT id FROM interview_questions WHERE user_id::text = auth.uid()::text
        )
    );
CREATE POLICY "Users can insert own interview answer" ON interview_answers
    FOR INSERT WITH CHECK (
        question_id IN (
            SELECT id FROM interview_questions WHERE user_id::text = auth.uid()::text
        )
    );
CREATE POLICY "Users can update own interview answer" ON interview_answers
    FOR UPDATE USING (
        question_id IN (
            SELECT id FROM interview_questions WHERE user_id::text = auth.uid()::text
        )
    );

-- ============================================================
-- Practice questions table policies
-- ============================================================
CREATE POLICY "Users can view own practice questions" ON practice_questions
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own practice question" ON practice_questions
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);

-- ============================================================
-- Practice attempts table policies
-- ============================================================
CREATE POLICY "Users can view own practice attempts" ON practice_attempts
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own practice attempt" ON practice_attempts
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY "Users can update own practice attempt" ON practice_attempts
    FOR UPDATE USING (user_id::text = auth.uid()::text);

-- ============================================================
-- Coding submissions table policies
-- ============================================================
CREATE POLICY "Users can view own coding submissions" ON coding_submissions
    FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY "Users can insert own coding submission" ON coding_submissions
    FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY "Users can update own coding submission" ON coding_submissions
    FOR UPDATE USING (user_id::text = auth.uid()::text);

-- ============================================================
-- Table grants for authenticated role
-- ============================================================
GRANT ALL ON profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE ON resumes TO authenticated;
GRANT SELECT, INSERT, UPDATE ON resume_analyses TO authenticated;
GRANT SELECT, INSERT, UPDATE ON job_analyses TO authenticated;
GRANT SELECT, INSERT, UPDATE ON job_matches TO authenticated;
GRANT SELECT, INSERT, UPDATE ON interview_sessions TO authenticated;
GRANT SELECT ON interview_questions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON interview_answers TO authenticated;
GRANT SELECT, INSERT ON practice_questions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON practice_attempts TO authenticated;
GRANT SELECT, INSERT, UPDATE ON coding_submissions TO authenticated;