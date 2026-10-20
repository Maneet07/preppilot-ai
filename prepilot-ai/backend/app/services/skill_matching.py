import json
import logging
from typing import Dict, List, Any, Optional
from google import genai

logger = logging.getLogger(__name__)


class SkillMatchingService:
    """Service for matching resume skills to job requirements using Gemini."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def _build_matching_prompt(self, resume_text: str, job_analysis: Dict[str, Any]) -> str:
        """Build a focused prompt for skill matching."""
        required_skills = job_analysis.get("required_skills", [])
        preferred_skills = job_analysis.get("preferred_skills", [])
        important_keywords = job_analysis.get("important_keywords", [])
        
        return f"""
You are an expert career coach conducting a skills gap analysis. Compare the following resume against a job description and provide a matching assessment.

Resume text:
---BEGIN RESUME---
{resume_text}
---END RESUME---

Job description analysis:
- Required skills: {', '.join(required_skills) if required_skills else 'None listed'}
- Preferred skills: {', '.join(preferred_skills) if preferred_skills else 'None listed'}
- Important keywords: {', '.join(important_keywords) if important_keywords else 'None listed'}

Provide your analysis in JSON format with exactly these keys:
{{
  "matched_skills": array of strings (skills the candidate has that are required),
  "missing_skills": array of strings (required skills the candidate lacks),
  "relevant_projects": array of strings (projects from resume that match),
  "evidence": array of strings (brief evidence for each matched skill),
  "compatibility_score": integer (0-100, approximate match percentage),
  "recommendations": array of strings (actionable improvement suggestions),
  "match_json": object with additional details
}}

Guidelines:
- matched_skills should only include skills that are in the required skills list AND present in the resume
- missing_skills should only include required skills that are NOT in the resume
- compatibility_score is an approximate heuristic, NOT an official ATS score or employer decision
- recommendations should be specific and actionable
- match_json can include additional metadata like skill coverage percentage, experience alignment, etc.

Be honest and accurate. If the resume doesn't match well, state that clearly with specific reasons. Do not inflate the compatibility score.
"""
    
    def match(self, resume_text: str, job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Match resume skills against job analysis and return results."""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty or contains only whitespace")
        
        if not job_analysis:
            raise ValueError("Job analysis is required for matching")
        
        try:
            prompt = self._build_matching_prompt(resume_text, job_analysis)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Try to parse the JSON response
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["matched_skills", "missing_skills", "relevant_projects",
                             "evidence", "compatibility_score", "recommendations",
                             "match_json"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate compatibility_score range
            if not isinstance(result["compatibility_score"], int) or result["compatibility_score"] < 0 or result["compatibility_score"] > 100:
                raise ValueError("Compatibility score must be an integer between 0 and 100")
            
            # Ensure arrays are actually arrays
            for field in ["matched_skills", "missing_skills", "relevant_projects", "evidence", "recommendations"]:
                if not isinstance(result[field], list):
                    result[field] = []
            
            # Ensure match_json is an object
            if not isinstance(result["match_json"], dict):
                result["match_json"] = {}
            
            logger.info(f"Skill matching completed, compatibility score: {result['compatibility_score']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Skill matching failed: {e}")
            raise