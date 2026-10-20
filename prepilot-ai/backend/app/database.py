import os
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    UUID,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone

# Database URL from environment
# In Freebuff Sites, env.DB binding takes precedence; falls back to DATABASE_URL env var
# If neither is set, use a default SQLite file for development
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )
else:
    # No DATABASE_URL set - use SQLite file for development
    # In Freebuff Sites production, env.DB binding is used directly in route handlers
    engine = create_engine(
        "sqlite:///./dev.db",
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )

# Create session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


# Profile model
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    target_role = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False
    )


# Resume model
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False
    )


# Resume analysis model
class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    resume_id = Column(Integer, nullable=True)
    overall_score = Column(Integer, nullable=True)
    strengths = Column(JSON, nullable=True, default_factory=list)
    weaknesses = Column(JSON, nullable=True, default_factory=list)
    identified_skills = Column(JSON, nullable=True, default_factory=list)
    missing_skills = Column(JSON, nullable=True, default_factory=list)
    improvement_suggestions = Column(JSON, nullable=True, default_factory=list)
    analysis_json = Column(JSON, nullable=True, default_factory=list)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Job analysis model
class JobAnalysis(Base):
    __tablename__ = "job_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    job_title = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    job_description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=True, default_factory=list)
    preferred_skills = Column(JSON, nullable=True, default_factory=list)
    matched_skills = Column(JSON, nullable=True, default_factory=list)
    missing_skills = Column(JSON, nullable=True, default_factory=list)
    recommendations = Column(JSON, nullable=True, default_factory=list)
    analysis_json = Column(JSON, nullable=True, default_factory=list)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Job match model
class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    resume_id = Column(Integer, nullable=True)
    job_analysis_id = Column(Integer, nullable=True)
    compatibility_score = Column(Integer, nullable=True)
    matched_skills = Column(JSON, nullable=True, default_factory=list)
    missing_skills = Column(JSON, nullable=True, default_factory=list)
    recommendations = Column(JSON, nullable=True, default_factory=list)
    match_json = Column(JSON, nullable=True, default_factory=list)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Interview session model
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    interview_type = Column(String, nullable=False)
    target_role = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    total_questions = Column(Integer, nullable=True)
    overall_score = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False
    )


# Interview question model
class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=True)
    expected_topics = Column(JSON, nullable=True, default_factory=list)
    question_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Interview answer model
class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    question_id = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    answer_text = Column(Text, nullable=True)
    relevance_score = Column(Integer, nullable=True)
    technical_accuracy_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    completeness_score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    suggested_answer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Practice question model
class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=True)
    question_text = Column(Text, nullable=False)
    question_data = Column(JSON, nullable=True, default_factory=list)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Practice attempt model
class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    practice_question_id = Column(Integer, nullable=False)
    answer_text = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    completed_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)


# Coding submission model
class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    problem_title = Column(String, nullable=False)
    programming_language = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    submitted_code = Column(Text, nullable=False)
    review_json = Column(JSON, nullable=True, default_factory=list)
    created_at = Column(DateTime(timezone=True), default=get_current_timestamp, nullable=False)
