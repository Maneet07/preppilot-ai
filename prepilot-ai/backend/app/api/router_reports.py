from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.schemas import ApiResponse, ReportResponse
from app.database import get_db, ResumeAnalysis, JobAnalysis, InterviewSession


router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get("/resume-analyses", response_model=List[ReportResponse], summary="Get resume analysis reports")
async def get_resume_analysis_reports(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all resume analysis reports for the current user."""
    analyses = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == user["id"]
    ).offset(skip).limit(limit).all()
    
    reports = []
    for analysis in analyses:
        reports.append(ReportResponse(
            id=analysis.id,
            user_id=user["id"],
            title=f"Resume Analysis - {analysis.created_at.strftime('%Y-%m-%d')}",
            type="resume_analysis",
            created_at=analysis.created_at,
            data={
                "overall_score": analysis.overall_score,
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses,
                "identified_skills": analysis.identified_skills,
                "missing_skills": analysis.missing_skills,
                "improvement_suggestions": analysis.improvement_suggestions,
            }
        ))
    
    return reports


@router.get("/job-analyses", response_model=List[ReportResponse], summary="Get job analysis reports")
async def get_job_analysis_reports(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all job analysis reports for the current user."""
    analyses = db.query(JobAnalysis).filter(
        JobAnalysis.user_id == user["id"]
    ).offset(skip).limit(limit).all()
    
    reports = []
    for analysis in analyses:
        reports.append(ReportResponse(
            id=analysis.id,
            user_id=user["id"],
            title=f"Job Analysis - {analysis.job_title or 'Unknown'} at {analysis.company_name or 'Unknown'}",
            type="job_analysis",
            created_at=analysis.created_at,
            data={
                "job_title": analysis.job_title,
                "company_name": analysis.company_name,
                "required_skills": analysis.required_skills,
                "matched_skills": analysis.matched_skills,
                "missing_skills": analysis.missing_skills,
                "recommendations": analysis.recommendations,
            }
        ))
    
    return reports


@router.get("/interview-history", response_model=List[ReportResponse], summary="Get interview history reports")
async def get_interview_history_reports(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get interview history reports for the current user."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user["id"]
    ).offset(skip).limit(limit).all()
    
    reports = []
    for session in sessions:
        # Get answers for this session
        answers = db.query(InterviewAnswer).filter(
            InterviewAnswer.session_id == session.id
        ).all()
        
        reports.append(ReportResponse(
            id=session.id,
            user_id=user["id"],
            title=f"{session.interview_type.title()} Interview - {session.target_role or 'Unknown Role'}",
            type="interview_session",
            created_at=session.created_at,
            data={
                "session_id": session.id,
                "interview_type": session.interview_type,
                "target_role": session.target_role,
                "difficulty": session.difficulty,
                "status": session.status,
                "total_questions": session.total_questions,
                "overall_score": session.overall_score,
                "answer_count": len(answers),
            }
        ))
    
    return reports