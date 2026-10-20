import logging
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import docx
except ImportError:
    docx = None

from google import genai
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class ResumeAnalysisResult(BaseModel):
    """Structured result from resume Gemini analysis."""
    overall_score: int = Field(default=0, ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = Field(default=None)
    education: List[str] = Field(default_factory=list)
    recommended_roles: List[str] = Field(default_factory=list)


class InterviewQuestion(BaseModel):
    """Structured interview question from Gemini."""
    question_text: str = Field(min_length=1)
    question_category: str = Field(default="technical")
    difficulty: str = Field(default="medium")
    relevance_explanation: str = Field(min_length=1)
    expected_answer_points: List[str] = Field(default_factory=list)


class InterviewQuestionsWrapper(BaseModel):
    """Wrapper for interview questions list."""
    questions: List[InterviewQuestion]


class AnswerEvaluation(BaseModel):
    """Structured answer evaluation from Gemini."""
    score: int = Field(ge=1, le=10)
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    missing_important_points: List[str] = Field(default_factory=list)
    stronger_answer_outline: str = Field(min_length=1)
    actionable_recommendations: List[str] = Field(default_factory=list)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) not available")
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    if docx is None:
        raise ImportError("python-docx not available")
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise


def extract_resume_text(file_path: str) -> str:
    """Extract text from resume file (PDF or DOCX)."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


class ResumeAnalysisService:
    """Service for analyzing resumes using Gemini AI."""
    
    def __init__(self, api_key: str, model: str = "gemini-3.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def _build_analysis_prompt(self, resume_text: str) -> str:
        """Build the prompt for Gemini resume analysis."""
        return f"""You are an expert HR consultant and technical recruiter. Analyze the following resume and provide a comprehensive assessment.

Resume text:
{resume_text}

Please provide analysis in JSON format with these fields:
- overall_score: integer from 0-100 representing candidate strength
- strengths: array of 3-5 key strengths
- missing_skills: array of 3-5 important skills gaps
- improvement_suggestions: array of 3-5 suggestions for improvement
- experience_years: integer or null (estimated total years)
- education: array of degree/diploma names
- recommended_roles: array of 3-5 job roles this candidate is suited for

Guidelines:
- overall_score should be 0-100 based on complete profile
- strengths should be specific and verifiable from the resume
- missing_skills should be technical or soft skills that would improve the candidate
- improvement_suggestions should be actionable and specific
- experience_years should be estimated total professional experience
- education should list highest degrees first
- recommended_roles should match the candidate's skill set and experience

Return ONLY valid JSON. No surrounding text, no explanations, no markdown formatting.
"""
    
    def _build_questions_prompt(self, resume_text: str, job_description: str = None) -> str:
        """Build the prompt for Gemini to generate interview questions."""
        job_context = ""
        if job_description:
            job_context = f"""

Job Description:
{job_description}

Generate questions that specifically address how the candidate's experience matches this job requirements."""
        
        return f"""You are an expert technical interviewer. Based on the following resume, generate personalized interview questions.

Resume text:
{resume_text}
{job_context}

Generate 5-7 interview questions that are:
1. Personalized to the candidate's actual skills, projects, and experience (DO NOT invent experience or skills)
2. Cover different categories: technical, HR, project-based, and behavioral
3. Appropriate difficulty level (easy, medium, or hard) based on the candidate's experience level
4. Each question should have:
   - question_text: the full question text
   - question_category: HR, technical, project-based, or behavioral
   - difficulty: easy, medium, or hard
   - relevance_explanation: why this question is relevant to this specific candidate
   - expected_answer_points: 3-5 key points the candidate should cover

Return a valid JSON array of question objects. No surrounding text, no explanations, no markdown formatting.
"""
    
    def _build_evaluation_prompt(self, question_text: str, candidate_answer: str, question_category: str = "technical") -> str:
        """Build the prompt for Gemini to evaluate an answer."""
        return f"""You are an expert {question_category} interviewer evaluating a candidate's answer.

Question: {question_text}
Candidate's answer: {candidate_answer}

Evaluate the answer based on these criteria:
- Technical correctness (for technical questions)
- Relevance and completeness
- Quality of explanation and reasoning
- Practical examples provided
- Communication clarity

Provide a score from 1-10 (1 being poor, 10 being excellent) and structured feedback:
- strengths: what the candidate did well
- areas_for_improvement: what could be improved
- missing_important_points: key points that were omitted
- stronger_answer_outline: a suggested better answer structure
- actionable_recommendations: 3-5 specific recommendations for improvement

Return a valid JSON object matching this schema. No surrounding text, no explanations, no markdown formatting.
"""
    
    def analyze_resume(self, resume_text: str) -> ResumeAnalysisResult:
        """Analyze resume text and return structured results."""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty or contains only whitespace")
        
        if len(resume_text) < 50:
            raise ValueError("Resume text too short for meaningful analysis")
        
        prompt = self._build_analysis_prompt(resume_text)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ResumeAnalysisResult,
                    "temperature": 0.2,
                }
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse and validate with Pydantic
            result = ResumeAnalysisResult.model_validate_json(response.text)
            logger.info(f"Resume analysis completed: score={result.overall_score}")
            return result
            
        except ValidationError as e:
            logger.warning(f"Gemini returned invalid ResumeAnalysisResult JSON: {e}")
            raise ValueError(f"AI returned malformed analysis: {str(e)}")
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            raise
    
    def generate_questions(self, resume_text: str, job_description: str = None) -> List[Dict[str, Any]]:
        """Generate personalized interview questions based on resume and optional job description."""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty or contains only whitespace")
        
        prompt = self._build_questions_prompt(resume_text, job_description)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": InterviewQuestionsWrapper,
                    "temperature": 0.3,
                }
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse and validate with Pydantic
            wrapper = InterviewQuestionsWrapper.model_validate_json(response.text)
            questions = wrapper.questions
            logger.info(f"Generated {len(questions)} interview questions")
            return questions
            
        except ValidationError as e:
            logger.warning(f"Gemini returned invalid interview questions JSON: {e}")
            raise ValueError(f"AI returned malformed questions: {str(e)}")
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            raise
    
    def evaluate_answer(self, question_text: str, candidate_answer: str, question_category: str = "technical") -> Dict[str, Any]:
        """Evaluate a candidate's answer to an interview question."""
        if not question_text or not question_text.strip():
            raise ValueError("Question text is empty")
        
        if not candidate_answer or not candidate_answer.strip():
            raise ValueError("Candidate answer is empty")
        
        prompt = self._build_evaluation_prompt(question_text, candidate_answer, question_category)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AnswerEvaluation,
                    "temperature": 0.2,
                }
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse and validate with Pydantic
            evaluation = AnswerEvaluation.model_validate_json(response.text)
            logger.info(f"Answer evaluated: score={evaluation.score}")
            return evaluation.model_dump()
            
        except ValidationError as e:
            logger.warning(f"Gemini returned invalid answer evaluation JSON: {e}")
            raise ValueError(f"AI returned malformed evaluation: {str(e)}")
        except Exception as e:
            logger.error(f"Answer evaluation failed: {e}")
            raise