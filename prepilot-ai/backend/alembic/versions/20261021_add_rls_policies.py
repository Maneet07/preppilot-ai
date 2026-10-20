"""Add RLS Policies Migration for PrepPilot AI

Revision ID: 20261021_add_rls_policies
Create Date: 2026-10-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20261021_add_rls_policies"
down_revision = "20261020_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add RLS policies on all tables."""

    # Enable Row Level Security on all tables
    op.execute("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE resume_analyses ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE job_analyses ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE job_matches ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE interview_questions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE interview_answers ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE practice_questions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE practice_attempts ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE coding_submissions ENABLE ROW LEVEL SECURITY;")

    # Profiles table policies
    op.execute(
        "CREATE POLICY \"Users can view own profile\" ON profiles "
        "FOR SELECT USING (auth.uid() = id);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own profile\" ON profiles "
        "FOR INSERT WITH CHECK (auth.uid() = id);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own profile\" ON profiles "
        "FOR UPDATE USING (auth.uid() = id);"
    )

    # Resumes table policies
    op.execute(
        "CREATE POLICY \"Users can view own resumes\" ON resumes "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own resume\" ON resumes "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own resume\" ON resumes "
        "FOR UPDATE USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can delete own resume\" ON resumes "
        "FOR DELETE USING (user_id::text = auth.uid()::text);"
    )

    # Resume analyses table policies
    op.execute(
        "CREATE POLICY \"Users can view own resume analyses\" ON resume_analyses "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can view analyses by resume\" ON resume_analyses "
        "FOR SELECT USING (resume_id IN (\n"
        "    SELECT id FROM resumes WHERE user_id::text = auth.uid()::text\n"
        "));"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own analysis\" ON resume_analyses "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )

    # Job analyses table policies
    op.execute(
        "CREATE POLICY \"Users can view own job analyses\" ON job_analyses "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own job analysis\" ON job_analyses "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own job analysis\" ON job_analyses "
        "FOR UPDATE USING (user_id::text = auth.uid()::text);"
    )

    # Job matches table policies
    op.execute(
        "CREATE POLICY \"Users can view own job matches\" ON job_matches "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own job match\" ON job_matches "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own job match\" ON job_matches "
        "FOR UPDATE USING (user_id::text = auth.uid()::text);"
    )

    # Interview sessions table policies
    op.execute(
        "CREATE POLICY \"Users can view own interview sessions\" ON interview_sessions "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own interview session\" ON interview_sessions "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own interview session\" ON interview_sessions "
        "FOR UPDATE USING (user_id::text = auth.uid()::text);"
    )

    # Interview questions table policies
    op.execute(
        "CREATE POLICY \"Users can view own interview questions\" ON interview_questions "
        "FOR SELECT USING (\n"
        "    session_id IN ("
        "        SELECT id FROM interview_sessions WHERE user_id::text = auth.uid()::text"
        "    )"
        ");"
    )

    # Interview answers table policies
    op.execute(
        "CREATE POLICY \"Users can view own interview answers\" ON interview_answers "
        "FOR SELECT USING (\n"
        "    question_id IN ("
        "        SELECT id FROM interview_questions WHERE user_id::text = auth.uid()::text"
        "    )"
        ");"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own interview answer\" ON interview_answers "
        "FOR INSERT WITH CHECK (\n"
        "    question_id IN ("
        "        SELECT id FROM interview_questions WHERE user_id::text = auth.uid()::text"
        "    )"
        ");"
    )
    op.execute(
        "CREATE POLICY \"Users can update own interview answer\" ON interview_answers "
        "FOR UPDATE USING (\n"
        "    question_id IN ("
        "        SELECT id FROM interview_questions WHERE user_id::text = auth.uid()::text"
        "    )"
        ");"
    )

    # Practice questions table policies
    op.execute(
        "CREATE POLICY \"Users can view own practice questions\" ON practice_questions "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own practice question\" ON practice_questions "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )

    # Practice attempts table policies
    op.execute(
        "CREATE POLICY \"Users can view own practice attempts\" ON practice_attempts "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own practice attempt\" ON practice_attempts "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own practice attempt\" ON practice_attempts "
        "FOR UPDATE USING (user_id::text = auth.uid()::text);"
    )

    # Coding submissions table policies
    op.execute(
        "CREATE POLICY \"Users can view own coding submissions\" ON coding_submissions "
        "FOR SELECT USING (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can insert own coding submission\" ON coding_submissions "
        "FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);"
    )
    op.execute(
        "CREATE POLICY \"Users can update own coding submission\" ON coding_submissions "
        "FOR UPDATE USING (user_id::text = auth.uid()::text);"
    )


def downgrade() -> None:
    """Drop RLS policies and disable Row Level Security."""

    # Drop all policies first, then disable RLS
    op.execute("ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE resumes DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE resume_analyses DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE job_analyses DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE job_matches DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE interview_sessions DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE interview_questions DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE interview_answers DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE practice_questions DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE practice_attempts DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE coding_submissions DISABLE ROW LEVEL SECURITY;")

    # Drop all policies
    op.execute("DROP POLICY IF EXISTS \"Users can view own profile\" ON profiles;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own profile\" ON profiles;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own profile\" ON profiles;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own resumes\" ON resumes;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own resume\" ON resumes;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own resume\" ON resumes;")
    op.execute("DROP POLICY IF EXISTS \"Users can delete own resume\" ON resumes;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own resume analyses\" ON resume_analyses;")
    op.execute("DROP POLICY IF EXISTS \"Users can view analyses by resume\" ON resume_analyses;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own analysis\" ON resume_analyses;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own job analyses\" ON job_analyses;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own job analysis\" ON job_analyses;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own job analysis\" ON job_analyses;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own job matches\" ON job_matches;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own job match\" ON job_matches;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own job match\" ON job_matches;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own interview sessions\" ON interview_sessions;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own interview session\" ON interview_sessions;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own interview session\" ON interview_sessions;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own interview questions\" ON interview_questions;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own interview answers\" ON interview_answers;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own interview answer\" ON interview_answers;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own interview answer\" ON interview_answers;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own practice questions\" ON practice_questions;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own practice question\" ON practice_questions;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own practice question\" ON practice_questions;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own practice attempts\" ON practice_attempts;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own practice attempt\" ON practice_attempts;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own practice attempt\" ON practice_attempts;")
    op.execute("DROP POLICY IF EXISTS \"Users can view own coding submissions\" ON coding_submissions;")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own coding submission\" ON coding_submissions;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own coding submission\" ON coding_submissions;")