import json
import os
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.schemas import (
    PracticeQuestionCreate, PracticeQuestionResponse,
    PracticeAttemptCreate, PracticeAttemptResponse,
    ApiResponse
)
from app.core.auth import get_current_user
from app.database import get_db, PracticeQuestion, PracticeAttempt
from app.services.technical_practice import TechnicalPracticeService

router = APIRouter(prefix="/v1/practice", tags=["practice"])

practice_service = TechnicalPracticeService(
    api_key=os.getenv("GEMINI_API_KEY", ""),
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)


@router.post("/questions/generate", response_model=PracticeQuestionResponse, summary="Generate practice question")
async def generate_practice_question(
    topic: str = Body(...),
    difficulty: str = Body("junior"),
    language: str = Body("Python"),
    experience_level: str = Body("junior"),
    focus_areas: Optional[List[str]] = Body(None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a technical practice question using Gemini AI."""
    # Create practice question record
    question = PracticeQuestion(
        user_id=user["id"],
        topic=topic,
        difficulty=difficulty,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    # Generate question content with Gemini
    try:
        generated = practice_service.generate_question(
            topic=topic,
            difficulty=difficulty,
            language=language,
            experience_level=experience_level,
            focus_areas=focus_areas,
        )
        
        # Update the question with generated content
        question_data_json = json.loads(json.dumps(generated.get("question_data", {})))
        question.question_data = generated
        db.commit()
        db.refresh(question)
        
        return {
            "id": question.id,
            "user_id": user["id"],
            "topic": question.topic,
            "difficulty": question.difficulty,
            "question_text": generated.get("question_text", ""),
            "question_data": question_data_json,
            "hint": generated.get("hint", ""),
            "difficulty": generated.get("difficulty", difficulty),
            "topic": generated.get("topic", topic),
            "created_at": question.created_at,
        }
    except Exception as e:
        # Still save the question record, just without generated content
        question.question_data = {"error": str(e)}
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate question: {str(e)}"
        )


@router.post("/attempts", response_model=PracticeAttemptResponse, summary="Submit practice attempt")
async def submit_practice_attempt(
    attempt_data: PracticeAttemptCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a practice attempt and get feedback."""
    # Get the practice question
    question = db.query(PracticeQuestion).filter(
        PracticeQuestion.id == attempt_data.practice_question_id,
        PracticeQuestion.user_id == user["id"]
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Practice question not found")
    
    # Get feedback from Gemini
    try:
        explanation = practice_service.get_explanation(
            question_text=question.question_text,
            question_data=question.question_data or {},
            solution=question.question_data.get("solution", {}) if question.question_data else {},
            language=language or "Python",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get explanation: {str(e)}"
        )
    
    # Create practice attempt record
    attempt = PracticeAttempt(
        user_id=user["id"],
        practice_question_id=attempt_data.practice_question_id,
        answer_text=attempt_data.answer_text,
        feedback=explanation.get("feedback", "No feedback available"),
        score=explanation.get("overall_score"),  # May need to extract from feedback
        completed_at=datetime.now(),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt