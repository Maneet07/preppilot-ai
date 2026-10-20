import json
import logging
from typing import Dict, List, Any, Optional
from google import genai

logger = logging.getLogger(__name__)


class JobAnalysisService:
    """Service for analyzing job descriptions using Google Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def _build_analysis_prompt(self, job_description: str, job_title: str = "", company_name: str = "") -> str:
        """Build a focused prompt for job description analysis."""
        return f"""
You are an expert technical recruiter and career coach. Analyze the following job description and provide a comprehensive breakdown.

Job description:
---BEGIN JOB DESCRIPTION---
{job_description}
---END JOB DESCRIPTION---

Additional context:
- Job title: {job_title}
- Company: {company_name}

Provide your analysis in JSON format with exactly these keys:
{{
  "required_skills": array of strings,
  "preferred_skills": array of strings,
  "responsibilities": array of strings,
  "experience_requirements": string,
  "education_certification_requirements": array of strings,
  "important_keywords": array of strings,
  "technical_competencies": array of strings,
  "communication_behavioral_competencies": array of strings,
  "analysis_json": object with additional details
}}

Guidelines:
- required_skills should list essential, must-have skills
- preferred_skills should list nice-to-have skills
- responsibilities should summarize key job responsibilities
- experience_requirements should specify years and level
- education_certification_requirements should list degrees and certifications
- important_keywords should include terms relevant for ATS filtering
- technical_competencies should focus on technical/programming skills
- communication_behavioral_competencies should cover soft skills and behavioral traits
- analysis_json can include additional metadata like seniority level, industry, etc.

Be thorough and accurate. Only include skills and competencies that are actually present in the job description.
"""
    
    def analyze(self, job_description: str, job_title: str = "", company_name: str = "") -> Dict[str, Any]:
        """Analyze a job description and return structured results."""
        if not job_description or not job_description.strip():
            raise ValueError("Job description is empty or contains only whitespace")
        
        if len(job_description) < 30:
            raise ValueError("Job description too short for meaningful analysis")
        
        try:
            prompt = self._build_analysis_prompt(job_description, job_title, company_name)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Try to parse the JSON response
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["required_skills", "preferred_skills", "responsibilities",
                             "experience_requirements", "education_certification_requirements",
                             "important_keywords", "technical_competencies",
                             "communication_behavioral_competencies", "analysis_json"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure arrays are actually arrays
            for field in ["required_skills", "preferred_skills", "responsibilities",
                         "education_certification_requirements", "important_keywords",
                         "technical_competencies", "communication_behavioral_competencies"]:
                if not isinstance(result[field], list):
                    result[field] = []
            
            # Ensure analysis_json is an object
            if not isinstance(result["analysis_json"], dict):
                result["analysis_json"] = {}
            
            logger.info(f"Job analysis completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Job analysis failed: {e}")
            raise