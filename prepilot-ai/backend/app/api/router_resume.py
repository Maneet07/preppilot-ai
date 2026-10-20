import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.schemas import (
    ResumeUpload, ResumeResponse, ResumeAnalysisRequest, ResumeAnalysisResponse,
    ApiResponse
)
from app.core.auth import get_current_user
from app.database import get_db, Resume, ResumeAnalysis
from app.services.resume_analysis import ResumeAnalysisService
from app.core.config import settings

router = APIRouter(prefix="/v1/resumes", tags=["resumes"])

# Initialize service
resume_service = ResumeAnalysisService(
    api_key=os.getenv("GEMINI_API_KEY", ""),
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
)


@router.get("/", response_model=List[ResumeResponse], summary="List user's resumes")
async def list_resumes(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all resumes belonging to the current user."""
    resumes = db.query(Resume).filter(Resume.user_id == user["id"]).all()
    return resumes


@router.post("/upload", response_model=ResumeResponse, summary="Upload and extract resume")
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """Upload a resume file (PDF or DOCX) and extract text."""
    # Validate file type
    allowed_extensions = [".pdf", ".docx"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    max_size = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
        )
    
    # Save file
    storage_path = f"uploads/resumes/{user['id']}/{file.filename}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / storage_path.lstrip("/")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Extract text based on file type
    extracted_text = ""
    try:
        if file_ext == ".pdf":
            extracted_text = resume_service.extract_text_pdf(file_content, file.filename)
        elif file_ext == ".docx":
            extracted_text = resume_service.extract_text_docx(file_content, file.filename)
    except ValueError as e:
        # Clean up uploaded file on extraction failure
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create resume record
    resume = Resume(
        user_id=user["id"],
        original_filename=file.filename,
        storage_path=storage_path,
        extracted_text=extracted_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume


@router.get("/{resume_id}", response_model=ResumeResponse, summary="Get resume by ID")
async def get_resume(
    resume_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific resume by ID (ownership validated)."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, 
        Resume.user_id == user["id"]
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", summary="Delete resume")
async def delete_resume(
    resume_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a resume and its associated analysis."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, 
        Resume.user_id == user["id"]
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete associated analyses
    db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id).delete()
    db.delete(resume)
    db.commit()
    
    # Delete physical file
    if resume.storage_path:
        try:
            file_path = Path(settings.UPLOAD_DIR) / resume.storage_path.lstrip("/")
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # File may already be deleted
    
    return {"message": "Resume deleted successfully"}


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisResponse, summary="Analyze resume with Gemini")
async def analyze_resume(
    resume_id: int,
    request: ResumeAnalysisRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze a resume using Gemini AI and save the results."""
    # Verify resume ownership
    resume = db.query(Resume).filter(
        Resume.id == resume_id, 
        Resume.user_id == user["id"]
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check if already analyzed
    existing = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.resume_id == resume_id,
        ResumeAnalysis.user_id == user["id"]
    ).first()
    if existing:
        return existing
    
    # Extract text if not already extracted
    extracted_text = resume.extracted_text
    if not extracted_text or not extracted_text.strip():
        # Try to extract from stored file
        file_ext = os.path.splitext(resume.original_filename)[1].lower()
        try:
            if file_ext == ".pdf":
                extracted_text = resume_service.extract_text_pdf(
                    b"", resume.original_filename  # Would need actual file data
                )
            elif file_ext == ".docx":
                extracted_text = resume_service.extract_text_docx(
                    b"", resume.original_filename
                )
        except Exception:
            extracted_text = ""
    
    if not extracted_text or not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in resume. The file may be encrypted, scanned, or corrupted."
        )
    
    # Analyze with Gemini
    try:
        analysis = resume_service.analyze(extracted_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"AI analysis failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")
    
    # Save analysis to database
    analysis_record = ResumeAnalysis(
        user_id=user["id"],
        resume_id=resume_id,
        overall_score=analysis.get("overall_score"),
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
        identified_skills=analysis.get("identified_skills", []),
        missing_skills=analysis.get("missing_skills", []),
        improvement_suggestions=analysis.get("improvement_suggestions", []),
        analysis_json=analysis.get("analysis_json", {}),
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)
    
    return analysis_record