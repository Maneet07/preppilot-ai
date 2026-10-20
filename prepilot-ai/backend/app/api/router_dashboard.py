from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.auth import get_current_user

from app.core.schemas import DashboardMetrics, ApiResponse
from app.database import get_db, Resume, ResumeAnalysis, JobAnalysis, JobMatch, InterviewSession, InterviewAnswer


router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardMetrics, summary="Get dashboard metrics")
async def get_dashboard_metrics(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard metrics for the current user."""
    # Count resumes
    total_resumes = db.query(Resume).filter(Resume.user_id == user["id"]).count()
    
    # Count resume analyses
    total_analyses = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == user["id"]).count()
    
    # Count interview sessions
    total_interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == user["id"]
    ).count()
    
    # Count completed interviews
    completed_interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == user["id"],
        InterviewSession.status == "completed"
    ).count()
    
    # Calculate average score from completed interviews
    completed_sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user["id"],
        InterviewSession.status == "completed",
        InterviewSession.overall_score.isnot(None)
    ).all()
    
    average_score = 0.0
    if completed_sessions:
        total = sum(s.overall_score for s in completed_sessions if s.overall_score)
        count = len([s for s in completed_sessions if s.overall_score is not None])
        if count > 0:
            average_score = round(total / count, 2)
    
    # Get resume readiness score (from most recent analysis)
    resume_readiness_score = None
    latest_analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == user["id"]
    ).order_by(ResumeAnalysis.created_at.desc()).first()
    if latest_analysis and latest_analysis.overall_score is not None:
        resume_readiness_score = latest_analysis.overall_score
    
    # Count job matches
    total_matches = db.query(JobMatch).filter(JobMatch.user_id == user["id"]).count()
    
    return DashboardMetrics(
        total_interviews=total_interviews,
        completed_interviews=completed_interviews,
        average_score=average_score,
        resume_readiness_score=resume_readiness_score,
        total_resumes=total_resumes,
        total_analyses=total_analyses,
    )