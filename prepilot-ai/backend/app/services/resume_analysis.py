import json
import logging
from typing import Dict, List, Any, Optional
from google import genai

logger = logging.getLogger(__name__)


class ResumeAnalysisService:
    """Service for analyzing resumes using Google Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def _build_analysis_prompt(self, resume_text: str) -> str:
        """Build a focused prompt for resume analysis."""
        return f"""
You are an expert career coach and resume specialist. Analyze the following resume text thoroughly and provide a comprehensive assessment.

Resume text:
---BEGIN RESUME---
{resume_text}
---END RESUME---

Provide your analysis in JSON format with exactly these keys:
{{
  "overall_score": integer (0-100),
  "strengths": array of strings,
  "weaknesses": array of strings,
  "identified_skills": array of strings,
  "missing_skills": array of strings,
  "improvement_suggestions": array of strings,
  "analysis_json": object with additional details
}}

Guidelines:
- overall_score should be a heuristic assessment of resume readiness, NOT an official ATS score
- strengths should highlight genuine strong points
- weaknesses should identify real areas for improvement
- identified_skills should list skills actually present in the resume
- missing_skills should list relevant skills that could be added or emphasized
- improvement_suggestions should be actionable and specific
- analysis_json can include additional metadata like format assessment, keyword density, etc.

Be thorough but concise. Do not fabricate information. If the resume is very limited, state that clearly.
"""
    
    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """Analyze a resume and return structured results."""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty or contains only whitespace")
        
        if len(resume_text) < 50:
            raise ValueError("Resume text too short for meaningful analysis")
        
        try:
            prompt = self._build_analysis_prompt(resume_text)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Try to parse the JSON response
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["overall_score", "strengths", "weaknesses", 
                             "identified_skills", "missing_skills", 
                             "improvement_suggestions", "analysis_json"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate overall_score range
            if not isinstance(result["overall_score"], int) or result["overall_score"] < 0 or result["overall_score"] > 100:
                raise ValueError("Overall score must be an integer between 0 and 100")
            
            # Ensure arrays are actually arrays
            for field in ["strengths", "weaknesses", "identified_skills", 
                         "missing_skills", "improvement_suggestions"]:
                if not isinstance(result[field], list):
                    result[field] = []
            
            # Ensure analysis_json is an object
            if not isinstance(result["analysis_json"], dict):
                result["analysis_json"] = {}
            
            logger.info(f"Resume analysis completed successfully, score: {result['overall_score']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            raise
    
    def extract_text_pdf(self, file_data: bytes, filename: str) -> str:
        """Extract text from a PDF file using PyMuPDF."""
        import fitz
        
        try:
            document = fitz.open(stream=file_data, filetype="pdf")
            text = ""
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text += page.get_text("text")
            return text.strip()
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise ValueError(f"Could not extract text from PDF: {str(e)}")
    
    def extract_text_docx(self, file_data: bytes, filename: str) -> str:
        """Extract text from a DOCX file using python-docx."""
        from docx import Document
        
        try:
            doc = Document(file_data)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX text extraction failed: {e}")
            raise ValueError(f"Could not extract text from DOCX: {str(e)}")