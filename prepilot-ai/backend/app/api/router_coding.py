import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.schemas import (
    CodingSubmissionCreate, CodingSubmissionResponse,
    ApiResponse
)
from app.core.auth import get_current_user
from app.database import get_db, CodingSubmission
from app.services.technical_practice import TechnicalPracticeService

router = APIRouter(prefix="/v1/coding", tags=["coding"])

coding_service = TechnicalPracticeService(
    api_key=os.getenv("GEMINI_API_KEY", ""),
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)


@router.post("/review", response_model=CodingSubmissionResponse, summary="Review submitted code")
async def review_code(
    submission: CodingSubmissionCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Review submitted code using Gemini AI."""
    # Create coding submission record
    submission_record = CodingSubmission(
        user_id=user["id"],
        problem_title=submission.problem_title,
        programming_language=submission.programming_language,
        problem_statement=submission.problem_statement,
        submitted_code=submission.submitted_code,
    )
    db.add(submission_record)
    db.commit()
    db.refresh(submission_record)
    
    # Review code with Gemini
    try:
        review = coding_service.review_code(
            code=submission.submitted_code,
            problem_statement=submission.problem_statement,
            language=submission.programming_language,
        )
        
        # Save review to database
        submission_record.review_json = review
        db.commit()
        db.refresh(submission_record)
        
        return {
            "id": submission_record.id,
            "user_id": user["id"],
            "problem_title": submission_record.problem_title,
            "programming_language": submission_record.programming_language,
            "problem_statement": submission_record.problem_statement,
            "submitted_code": submission_record.submitted_code,
            "review_json": review,
            "created_at": submission_record.created_at,
        }
    except Exception as e:
        submission_record.review_json = {"error": str(e)}
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Code review failed: {str(e)}"
        )