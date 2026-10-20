import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.schemas import (
    JobAnalysisCreate, JobAnalysisRequest, JobAnalysisResponse,
    JobMatchCreate, JobMatchResponse, ApiResponse
)
from app.core.auth import get_current_user
from app.database import get_db, JobAnalysis, JobMatch
from app.services.job_analysis import JobAnalysisService
from app.services.skill_matching import SkillMatchingService

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])

job_analysis_service = JobAnalysisService(
    api_key=os.getenv("GEMINI_API_KEY", ""),
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)

skill_matching_service = SkillMatchingService(
    api_key=os.getenv("GEMINI_API_KEY", ""),
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)


@router.post("/analyze", response_model=JobAnalysisResponse, summary="Analyze job description")
async def analyze_job(
    job_data: JobAnalysisRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze a job description using Gemini AI."""
    # Analyze with Gemini
    try:
        analysis = job_analysis_service.analyze(
            job_description=job_data.job_description,
            job_title=job_data.job_title,
            company_name=job_data.company_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")
    
    # Save to database
    job_analysis = JobAnalysis(
        user_id=user["id"],
        job_title=job_data.job_title,
        company_name=job_data.company_name,
        job_description=job_data.job_description,
        required_skills=analysis.get("required_skills", []),
        preferred_skills=analysis.get("preferred_skills", []),
        matched_skills=analysis.get("matched_skills", []),
        missing_skills=analysis.get("missing_skills", []),
        recommendations=analysis.get("recommendations", []),
        analysis_json=analysis.get("analysis_json", {}),
    )
    db.add(job_analysis)
    db.commit()
    db.refresh(job_analysis)
    
    return job_analysis


@router.get("/", response_model=List[JobAnalysisResponse], summary="List user's job analyses")
async def list_job_analyses(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all job analyses belonging to the current user."""
    analyses = db.query(JobAnalysis).filter(
        JobAnalysis.user_id == user["id"]
    ).offset(skip).limit(limit).all()
    return analyses


@router.post("/match", response_model=JobMatchResponse, summary="Match resume to job")
async def match_resume_to_job(
    match_data: JobMatchCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Match a resume against a job analysis using Gemini AI."""
    # Verify resume ownership
    resume = db.query(Resume).filter(
        Resume.id == match_data.resume_id,
        Resume.user_id == user["id"]
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Verify job analysis ownership
    job_analysis = db.query(JobAnalysis).filter(
        JobAnalysis.id == match_data.job_analysis_id,
        JobAnalysis.user_id == user["id"]
    ).first()
    if not job_analysis:
        raise HTTPException(status_code=404, detail="Job analysis not found")
    
    # Get resume text for matching
    resume_text = resume.extracted_text or ""
    if not resume_text or not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume has no extracted text. Please ensure the resume has been analyzed."
        )
    
    # Perform skill matching
    try:
        match_result = skill_matching_service.match(
            resume_text=resume_text,
            job_analysis=job_analysis.model_dump() if hasattr(job_analysis, 'model_dump') 
            else {k: getattr(job_analysis, k) for k in [
                'required_skills', 'preferred_skills', 'matched_skills', 
                'missing_skills', 'recommendations', 'analysis_json'
            ]}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI matching error: {str(e)}")
    
    # Save match to database
    job_match = JobMatch(
        user_id=user["id"],
        resume_id=match_data.resume_id,
        job_analysis_id=match_data.job_analysis_id,
        compatibility_score=match_result.get("compatibility_score"),
        matched_skills=match_result.get("matched_skills", []),
        missing_skills=match_result.get("missing_skills", []),
        recommendations=match_result.get("recommendations", []),
        match_json=match_result.get("match_json", {}),
    )
    db.add(job_match)
    db.commit()
    db.refresh(job_match)
    
    return job_match