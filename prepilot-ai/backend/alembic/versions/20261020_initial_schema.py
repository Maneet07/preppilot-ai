"""Initial schema migration for PrepPilot AI

Revision ID: 20261020_initial
Create Date: 2026-10-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = "20261020_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for PrepPilot AI."""
    
    # Create profiles table
    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), nullable=False, default=uuid.uuid4),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("target_role", sa.String(), nullable=True),
        sa.Column("experience_level", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    
    # Create resumes table
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=False),
        sa.Column("storage_path", sa.String(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create resume_analyses table
    op.create_table(
        "resume_analyses",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=True),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("strengths", sa.JSON(), nullable=True),
        sa.Column("weaknesses", sa.JSON(), nullable=True),
        sa.Column("identified_skills", sa.JSON(), nullable=True),
        sa.Column("missing_skills", sa.JSON(), nullable=True),
        sa.Column("improvement_suggestions", sa.JSON(), nullable=True),
        sa.Column("analysis_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create job_analyses table
    op.create_table(
        "job_analyses",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("job_title", sa.String(), nullable=True),
        sa.Column("company_name", sa.String(), nullable=True),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=True),
        sa.Column("preferred_skills", sa.JSON(), nullable=True),
        sa.Column("matched_skills", sa.JSON(), nullable=True),
        sa.Column("missing_skills", sa.JSON(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("analysis_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create job_matches table
    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=True),
        sa.Column("job_analysis_id", sa.Integer(), nullable=True),
        sa.Column("compatibility_score", sa.Integer(), nullable=True),
        sa.Column("matched_skills", sa.JSON(), nullable=True),
        sa.Column("missing_skills", sa.JSON(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("match_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create interview_sessions table
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("interview_type", sa.String(), nullable=False),
        sa.Column("target_role", sa.String(), nullable=True),
        sa.Column("experience_level", sa.String(), nullable=True),
        sa.Column("difficulty", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("total_questions", sa.Integer(), nullable=True),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create interview_questions table
    op.create_table(
        "interview_questions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(), nullable=True),
        sa.Column("expected_topics", sa.JSON(), nullable=True),
        sa.Column("question_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create interview_answers table
    op.create_table(
        "interview_answers",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("relevance_score", sa.Integer(), nullable=True),
        sa.Column("technical_accuracy_score", sa.Integer(), nullable=True),
        sa.Column("communication_score", sa.Integer(), nullable=True),
        sa.Column("completeness_score", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("suggested_answer", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create practice_questions table
    op.create_table(
        "practice_questions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create practice_attempts table
    op.create_table(
        "practice_attempts",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("practice_question_id", sa.Integer(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create coding_submissions table
    op.create_table(
        "coding_submissions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("problem_title", sa.String(), nullable=False),
        sa.Column("programming_language", sa.String(), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False),
        sa.Column("submitted_code", sa.Text(), nullable=False),
        sa.Column("review_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes for performance
    op.create_index(
        "ix_resumes_user_id", "resumes", ["user_id"], unique=False
    )
    op.create_index(
        "ix_resume_analyses_user_id", "resume_analyses", ["user_id"], unique=False
    )
    op.create_index(
        "ix_resume_analyses_resume_id", "resume_analyses", ["resume_id"], unique=False
    )
    op.create_index(
        "ix_job_analyses_user_id", "job_analyses", ["user_id"], unique=False
    )
    op.create_index(
        "ix_job_matches_user_id", "job_matches", ["user_id"], unique=False
    )
    op.create_index(
        "ix_interview_sessions_user_id", "interview_sessions", ["user_id"], unique=False
    )
    op.create_index(
        "ix_interview_questions_session_id", "interview_questions", ["session_id"], unique=False
    )
    op.create_index(
        "ix_interview_answers_session_id", "interview_answers", ["session_id"], unique=False
    )
    op.create_index(
        "ix_practice_questions_user_id", "practice_questions", ["user_id"], unique=False
    )
    op.create_index(
        "ix_practice_attempts_user_id", "practice_attempts", ["user_id"], unique=False
    )
    op.create_index(
        "ix_coding_submissions_user_id", "coding_submissions", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Drop all tables for PrepPilot AI."""
    
    op.drop_index("ix_coding_submissions_user_id", table_name="coding_submissions")
    op.drop_index("ix_practice_attempts_user_id", table_name="practice_attempts")
    op.drop_index("ix_practice_questions_user_id", table_name="practice_questions")
    op.drop_index("ix_interview_answers_session_id", table_name="interview_answers")
    op.drop_index("ix_interview_questions_session_id", table_name="interview_questions")
    op.drop_index("ix_interview_sessions_user_id", table_name="interview_sessions")
    op.drop_index("ix_job_matches_user_id", table_name="job_matches")
    op.drop_index("ix_job_analyses_user_id", table_name="job_analyses")
    op.drop_index("ix_resume_analyses_resume_id", table_name="resume_analyses")
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    
    op.drop_table("coding_submissions")
    op.drop_table("practice_attempts")
    op.drop_table("practice_questions")
    op.drop_table("interview_answers")
    op.drop_table("interview_questions")
    op.drop_table("interview_sessions")
    op.drop_table("job_matches")
    op.drop_table("job_analyses")
    op.drop_table("resume_analyses")
    op.drop_table("resumes")
    op.drop_table("profiles")