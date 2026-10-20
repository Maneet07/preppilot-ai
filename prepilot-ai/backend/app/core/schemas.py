from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# ============ Authentication Schemas ============

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=30, alias="expires_in")


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ============ Profile Schemas ============

class ProfileCreate(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    full_name: Optional[str] = None
    email: str
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Resume Schemas ============

class ResumeUpload(BaseModel):
    original_filename: str
    file_size: int
    content_type: str


class ResumeResponse(BaseModel):
    id: int
    user_id: str
    original_filename: str
    storage_path: str
    extracted_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumeAnalysisRequest(BaseModel):
    resume_id: int


# ============ Resume Analysis Schemas ============

class ResumeAnalysisResponse(BaseModel):
    id: int
    user_id: str
    resume_id: Optional[int] = None
    overall_score: Optional[int] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    identified_skills: List[str] = []
    missing_skills: List[str] = []
    improvement_suggestions: List[str] = []
    analysis_json: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Job Analysis Schemas ============

class JobAnalysisCreate(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: str


class JobAnalysisRequest(BaseModel):
    job_description: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class JobAnalysisResponse(BaseModel):
    id: int
    user_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    recommendations: List[str] = []
    analysis_json: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Job Match Schemas ============

class JobMatchCreate(BaseModel):
    resume_id: int
    job_analysis_id: int


class JobMatchResponse(BaseModel):
    id: int
    user_id: str
    resume_id: Optional[int] = None
    job_analysis_id: Optional[int] = None
    compatibility_score: Optional[int] = None
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    recommendations: List[str] = []
    match_json: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Interview Session Schemas ============

class InterviewSessionCreate(BaseModel):
    interview_type: str
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    difficulty: Optional[str] = None


class InterviewSessionUpdate(BaseModel):
    status: Optional[str] = None
    overall_score: Optional[int] = None


class InterviewSessionResponse(BaseModel):
    id: int
    user_id: str
    interview_type: str
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    difficulty: Optional[str] = None
    status: str
    total_questions: Optional[int] = None
    overall_score: Optional[int] = None
    summary: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Interview Question Schemas ============

class InterviewQuestionCreate(BaseModel):
    question_text: str
    question_type: str = "technical"
    expected_topics: Optional[List[str]] = None


class InterviewQuestionResponse(BaseModel):
    id: int
    session_id: int
    user_id: str
    question_text: str
    question_type: str
    expected_topics: List[str]
    question_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Interview Answer Schemas ============

class InterviewAnswerCreate(BaseModel):
    answer_text: str


class InterviewAnswerResponse(BaseModel):
    id: int
    session_id: int
    question_id: int
    user_id: str
    answer_text: Optional[str] = None
    relevance_score: Optional[int] = None
    technical_accuracy_score: Optional[int] = None
    communication_score: Optional[int] = None
    completeness_score: Optional[int] = None
    feedback: Optional[str] = None
    suggested_answer: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Practice Question Schemas ============

class PracticeQuestionCreate(BaseModel):
    topic: str
    difficulty: str = "junior"


class PracticeQuestionResponse(BaseModel):
    id: int
    user_id: str
    topic: str
    difficulty: str
    question_text: str
    question_data: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Practice Attempt Schemas ============

class PracticeAttemptCreate(BaseModel):
    answer_text: str


class PracticeAttemptResponse(BaseModel):
    id: int
    user_id: str
    practice_question_id: int
    answer_text: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[int] = None
    completed_at: datetime
    
    class Config:
        from_attributes = True


# ============ Coding Submission Schemas ============

class CodingSubmissionCreate(BaseModel):
    problem_title: str
    programming_language: str
    problem_statement: str
    submitted_code: str


class CodingSubmissionResponse(BaseModel):
    id: int
    user_id: str
    problem_title: str
    programming_language: str
    problem_statement: str
    submitted_code: str
    review_json: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Dashboard Schemas ============

class DashboardMetrics(BaseModel):
    total_interviews: int = 0
    completed_interviews: int = 0
    average_score: float = 0.0
    resume_readiness_score: Optional[int] = None
    total_resumes: int = 0
    total_analyses: int = 0


# ============ Report Schemas ============

class ReportResponse(BaseModel):
    id: int
    user_id: str
    title: str
    type: str
    created_at: datetime
    data: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


# ============ API Response Schemas ============

class ApiResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = []


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[str] = []
    status_code: int