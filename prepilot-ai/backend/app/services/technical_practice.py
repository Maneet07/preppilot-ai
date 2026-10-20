import json
import logging
from typing import Dict, List, Any, Optional
from google import genai

logger = logging.getLogger(__name__)


class TechnicalPracticeService:
    """Service for generating technical practice questions and explanations using Gemini."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def _build_practice_prompt(self, topic: str, difficulty: str, 
                              language: str = "Python", 
                              experience_level: str = "junior",
                              focus_areas: List[str] = None) -> str:
        """Build a prompt for generating technical practice questions."""
        focus_str = ", ".join(focus_areas) if focus_areas else "general concepts"
        
        return f"""
You are an expert technical educator generating practice questions for a {experience_level} 
developer specializing in {topic}.

Candidate level: {experience_level}
Primary language: {language}
Focus areas: {focus_str}
Difficulty: {difficulty}

Generate one comprehensive practice question with the following structure:

{{
  "question_text": "the full practice question",
  "question_data": {{
    "constraints": ["string", "string"],
    "example_input": "string",
    "example_output": "string",
    "edge_cases": ["string", "string"]
  }},
  "hint": "a subtle hint to help if stuck (do not give away the solution)",
  "solution": {{
    "approach": "description of the recommended approach",
    "code": "complete, working solution in {language}",
    "complexity": {{
      "time": "Big O notation for time complexity",
      "space": "Big O notation for space complexity"
    }},
    "explanation": "step-by-step explanation of the solution"
  }},
  "difficulty": "{difficulty}",
  "topic": "{topic}"
}}

Guidelines:
- question_text should be clear, well-defined, and appropriate for the specified level
- question_data.constraints should list 3-5 specific constraints or requirements
- question_data.example_input should be a clear, testable input
- question_data.example_output should match the expected output for the example input
- question_data.edge_cases should list 2-3 edge cases to consider
- hint should be helpful without giving away the solution
- solution.code should be correct, production-quality {language} code
- solution.complexity should accurately reflect the code's performance
- solution.explanation should be educational and thorough
- Difficulty should match the requested level: junior (fundamental), mid (practical), senior (advanced/system design)
- Topic should be exactly: {topic}

Be specific and educational. The goal is to help the candidate learn and improve.
"""
    
    def generate_question(self, topic: str, difficulty: str, 
                       language: str = "Python", 
                       experience_level: str = "junior",
                       focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate a single technical practice question."""
        if not topic or not topic.strip():
            raise ValueError("Topic is required")
        
        valid_difficulties = ["junior", "mid", "senior"]
        if difficulty not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
        
        prompt = self._build_practice_prompt(topic, difficulty, language, experience_level, focus_areas)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse the JSON response
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["question_text", "question_data", "hint", "solution", 
                             "difficulty", "topic"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate question_data sub-fields
            qd = result.get("question_data", {})
            for field in ["constraints", "example_input", "example_output", "edge_cases"]:
                if field not in qd:
                    if field == "constraints":
                        qd[field] = []
                    elif field == "edge_cases":
                        qd[field] = []
                    else:
                        qd[field] = ""
            
            # Validate solution sub-fields
            solution = result.get("solution", {})
            for field in ["approach", "code", "complexity", "explanation"]:
                if field not in solution:
                    if field == "complexity":
                        solution[field] = {"time": "O(n)", "space": "O(1)"}
                    else:
                        solution[field] = "Not provided"
            
            # Ensure complexity has sub-fields
            complexity = solution.get("complexity", {})
            if "time" not in complexity:
                complexity["time"] = "O(n)"
            if "space" not in complexity:
                complexity["space"] = "O(1)"
            solution["complexity"] = complexity
            
            logger.info(f"Technical practice question generated for topic: {topic}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini practice question response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Technical practice question generation failed: {e}")
            raise
    
    def _build_explanation_prompt(self, question_text: str, question_data: Dict,
                                  solution: Dict, language: str = "Python") -> str:
        """Build a prompt for explaining a practice question."""
        return f"""
You are an expert technical educator providing an explanation for the following practice question.

Question: {question_text}

Constraints: {question_data.get('constraints', [])}
Example input: {question_data.get('example_input', '')}
Example output: {question_data.get('example_output', '')}

The solution is:
---BEGIN SOLUTION---
{solution.get('code', 'Not provided')}
---END SOLUTION---

Complexity: {solution.get('complexity', {}).get('time', 'O(n)')} time, 
{solution.get('complexity', {}).get('space', 'O(1)')} space

Provide a clear, educational explanation in JSON format:
{{
  "key_concepts": ["string", "string"],
  "step_by_step": ["string", "string"],
  "common_mistakes": ["string", "string"],
  "variations": ["string", "string"],
  "additional_resources": ["string", "string"]
}}

Guidelines:
- key_concepts should list 3-5 important concepts the candidate should understand
- step_by_step should break down the solution approach in 3-5 steps
- common_mistakes should list 2-3 pitfalls candidates often fall into
- variations should suggest 2-3 ways the question could be modified
- additional_resources should suggest learning materials (books, articles, tutorials)
- Keep it educational and practical
"""
    
    def get_explanation(self, question_text: str, question_data: Dict, 
                       solution: Dict, language: str = "Python") -> Dict[str, Any]:
        """Get an explanation for a practice question."""
        prompt = self._build_explanation_prompt(question_text, question_data, solution, language)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["key_concepts", "step_by_step", "common_mistakes",
                             "variations", "additional_resources"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure arrays are actually arrays
            for field in ["key_concepts", "step_by_step", "common_mistakes", 
                         "variations", "additional_resources"]:
                if not isinstance(result[field], list):
                    result[field] = []
            
            logger.info(f"Practice question explanation generated")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini explanation response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Practice explanation generation failed: {e}")
            raise
    
    def _build_code_review_prompt(self, code: str, problem_statement: str, 
                                  language: str = "Python") -> str:
        """Build a prompt for code review."""
        return f"""
You are an expert code reviewer reviewing the following {language} code.

Problem statement: {problem_statement}

Code to review:
---BEGIN CODE---
{code}
---END CODE---

Provide a code review in JSON format:
{{
  "review_summary": "string (overall assessment of the code)",
  "strengths": ["string", "string"],
  "improvements": ["string", "string"],
  "complexity_analysis": {{
    "time": "Big O notation",
    "space": "Big O notation"
  }},
  "suggested_refactoring": "string (specific refactoring suggestions)",
  "style_issues": ["string", "string"],
  "correctness_issues": ["string", "string"],
  "code_review_json": object with additional details
}}

Guidelines:
- review_summary should be a concise overall assessment
- strengths should highlight what the code does well
- improvements should be specific, actionable suggestions
- complexity_analysis should accurately analyze the code's performance
- suggested_refactoring should provide concrete refactoring steps
- style_issues should identify any style or formatting problems
- correctness_issues should flag any bugs or logical errors
- code_review_json can include additional metadata
- Be constructive and educational, not just critical
- Do not execute the code, perform static analysis only
"""
    
    def review_code(self, code: str, problem_statement: str, 
                    language: str = "Python") -> Dict[str, Any]:
        """Review submitted code using Gemini."""
        if not code or not code.strip():
            raise ValueError("Code is empty or contains only whitespace")
        
        if not problem_statement or not problem_statement.strip():
            raise ValueError("Problem statement is required")
        
        prompt = self._build_code_review_prompt(code, problem_statement, language)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["review_summary", "strengths", "improvements",
                             "complexity_analysis", "suggested_refactoring",
                             "style_issues", "correctness_issues", "code_review_json"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure complexity_analysis has sub-fields
            complexity = result.get("complexity_analysis", {})
            if "time" not in complexity:
                complexity["time"] = "Unable to determine"
            if "space" not in complexity:
                complexity["space"] = "Unable to determine"
            result["complexity_analysis"] = complexity
            
            # Ensure arrays are actually arrays
            for field in ["strengths", "improvements", "style_issues", "correctness_issues"]:
                if not isinstance(result[field], list):
                    result[field] = []
            
            # Ensure code_review_json is an object
            if not isinstance(result["code_review_json"], dict):
                result["code_review_json"] = {}
            
            logger.info(f"Code review completed")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini code review response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            raise