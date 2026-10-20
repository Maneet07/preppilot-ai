import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.schemas import (
    InterviewSessionCreate, InterviewSessionUpdate, InterviewSessionResponse,
    InterviewQuestionCreate, InterviewQuestionResponse,
    InterviewAnswerCreate, InterviewAnswerResponse,
    PracticeQuestionCreate, PracticeQuestionResponse,
    PracticeAttemptCreate, PracticeAttemptResponse,
    ApiResponse
)
from app.core.auth import get_current_user
from app.database import get_db, InterviewSession, InterviewQuestion, InterviewAnswer
from app.services.mock_interview import MockInterviewService

router = APIRouter(prefix="/v1/interviews", tags=["interviews"])

interview_service = MockInterviewService(
    api_key=os.getenv("GEMINI_API_KEY", ""),
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)


@router.post("/", response_model=InterviewSessionResponse, summary="Create new interview session")
async def create_interview_session(
    session_data: InterviewSessionCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new mock interview session."""
    session = InterviewSession(
        user_id=user["id"],
        interview_type=session_data.interview_type,
        target_role=session_data.target_role,
        experience_level=session_data.experience_level,
        difficulty=session_data.difficulty,
        status="pending",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Generate initial questions
    try:
        questions = interview_service.generate_questions(
            interview_type=session_data.interview_type,
            target_role=session_data.target_role or "",
            difficulty=session_data.difficulty or "mid",
            experience_level=session_data.experience_level or "junior",
        )
        
        # Save questions to database
        for i, q in enumerate(questions):
            question = InterviewQuestion(
                session_id=session.id,
                user_id=user["id"],
                question_text=q.get("question_text", ""),
                question_type=q.get("question_type", "technical"),
                expected_topics=q.get("expected_topics", []),
                question_order=i,
            )
            db.add(question)
        db.commit()
    except Exception as e:
        # Still create the session, just without questions initially
        logger.warning(f"Failed to generate initial questions: {e}")
    
    return session


@router.get("/", response_model=List[InterviewSessionResponse], summary="List user's interview sessions")
async def list_interview_sessions(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all interview sessions belonging to the current user."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user["id"]
    ).offset(skip).limit(limit).all()
    return sessions


@router.get("/{session_id}", response_model=InterviewSessionResponse, summary="Get interview session")
async def get_interview_session(
    session_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific interview session by ID."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user["id"]
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


@router.post("/{session_id}/next-question", summary="Get next interview question")
async def get_next_question(
    session_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the next unanswered question for an interview session."""
    # Get session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user["id"]
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Get unanswered questions
    asked_question_ids = db.query(InterviewAnswer.question_id).filter(
        InterviewAnswer.session_id == session_id
    ).subquery()
    
    next_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id,
        ~InterviewQuestion.id.in_(asked_question_ids)
    ).order_by(InterviewQuestion.question_order.asc()).first()
    
    if not next_question:
        # Interview complete
        session.status = "completed"
        session.completed_at = datetime.now()
        db.commit()
        return {"message": "Interview complete", "session": session}
    
    return {
        "question": {
            "id": next_question.id,
            "text": next_question.question_text,
            "type": next_question.question_type,
            "order": next_question.question_order,
        },
        "session_status": session.status,
    }


@router.post("/{session_id}/answers", response_model=InterviewAnswerResponse, summary="Submit answer")
async def submit_answer(
    session_id: int,
    question_id: int,
    answer_text: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an answer to an interview question and get evaluation."""
    # Verify question belongs to session
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.session_id == session_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Evaluate answer with Gemini
    try:
        evaluation = interview_service.evaluate_answer(
            question=question.question_text,
            question_type=question.question_type,
            expected_topics=question.expected_topics or [],
            answer=answer_text,
            difficulty=session.difficulty or "mid",
            target_role=session.target_role or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI evaluation error: {str(e)}")
    
    # Save answer to database
    answer = InterviewAnswer(
        session_id=session_id,
        question_id=question_id,
        user_id=user["id"],
        answer_text=answer_text,
        relevance_score=evaluation.get("relevance_score"),
        technical_accuracy_score=evaluation.get("technical_accuracy_score"),
        communication_score=evaluation.get("communication_score"),
        completeness_score=evaluation.get("completeness_score"),
        feedback=evaluation.get("feedback"),
        suggested_answer=evaluation.get("suggested_answer"),
    )
    db.add(answer)
    
    # Update session score tracking
    session.total_questions = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session_id
    ).count()
    
    db.commit()
    db.refresh(answer)
    
    return answer


@router.post("/{session_id}/complete", response_model=InterviewSessionResponse, summary="Complete interview session")
async def complete_interview_session(
    session_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Finalize an interview session and generate report."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user["id"]
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Calculate overall score
    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session_id
    ).all()
    
    if answers:
        total_score = sum(
            (a.relevance_score or 0) + (a.technical_accuracy_score or 0) + 
            (a.communication_score or 0) + (a.completeness_score or 0)
        ) / (len(answers) * 4)
        session.overall_score = round(total_score, 2)
    
    session.status = "completed"
    session.completed_at = datetime.now()
    db.commit()
    db.refresh(session)
    
    # Generate report
    all_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).all()
    all_answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session_id
    ).all()
    
    question_texts = [q.question_text for q in all_questions]
    answer_texts = [a.answer_text or "" for a in all_answers]
    scores = [
        {
            "relevance_score": a.relevance_score,
            "technical_accuracy_score": a.technical_accuracy_score,
            "communication_score": a.communication_score,
            "completeness_score": a.completeness_score,
        }
        for a in all_answers
    ]
    
    try:
        report = interview_service.generate_report(
            interview_type=session.interview_type,
            target_role=session.target_role or "",
            difficulty=session.difficulty or "mid",
            experience_level=session.experience_level or "junior",
            questions=[{
                "question_text": q.question_text,
                "question_type": q.question_type,
                "expected_topics": q.expected_topics or [],
            } for q in all_questions],
            answers=answer_texts,
            scores=scores,
            summary=session.summary or "",
        )
        
        session.summary = str(report.get("overall_score", 0))  # Store summary field
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to generate interview report: {e}")
    
    return session


@router.get("/{session_id}/report", summary="Get interview report")
async def get_interview_report(
    session_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the interview report for a completed session."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user["id"]
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Get all questions and answers
    all_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).all()
    all_answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session_id
    ).all()
    
    question_texts = [q.question_text for q in all_questions]
    answer_texts = [a.answer_text or "" for a in all_answers]
    
    # Get scores
    scores = []
    for a in all_answers:
        scores.append({
            "relevance_score": a.relevance_score,
            "technical_accuracy_score": a.technical_accuracy_score,
            "communication_score": a.communication_score,
            "completeness_score": a.completeness_score,
        })
    
    return {
        "session": session,
        "questions": question_texts,
        "answers": answer_texts,
        "answers_with_evaluation": [
            {
                "id": a.id,
                "relevance_score": a.relevance_score,
                "technical_accuracy_score": a.technical_accuracy_score,
                "communication_score": a.communication_score,
                "completeness_score": a.completeness_score,
                "feedback": a.feedback,
                "suggested_answer": a.suggested_answer,
            }
            for a in all_answers
        ],
    }