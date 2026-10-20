import json
import logging
from typing import Dict, List, Any, Optional
from google import genai

logger = logging.getLogger(__name__)


class MockInterviewService:
    """Service for generating mock interview questions and evaluating answers using Gemini."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def _build_question_prompt(self, interview_type: str, target_role: str, 
                              difficulty: str, experience_level: str, 
                              job_description: str = "", resume_context: str = "") -> str:
        """Build a prompt for generating interview questions."""
        return f"""
You are an expert interviewer conducting a {interview_type} interview for a {target_role} position.

Candidate information:
- Experience level: {experience_level}
- Difficulty: {difficulty}
- Target role: {target_role}

Additional context:
- Job description: {job_description if job_description else 'Not provided'}
- Resume context: {resume_context if resume_context else 'Not provided'}

Generate {self._get_question_count(interview_type)} interview questions, one at a time.

For each question, provide:
- question_text: the full question text
- question_type: technical, behavioral, or situational
- expected_topics: array of key topics or concepts the candidate should address
- difficulty: match the requested difficulty level

Format the output as a JSON array of question objects:
{{
  "question_text": "string",
  "question_type": "technical|behavioral|situational",
  "expected_topics": ["string", "string"],
  "difficulty": "string"
}}

Difficulty guidelines:
- junior: 0-2 years experience, fundamental concepts
- mid: 2-5 years experience, practical application
- senior: 5+ years experience, system design, leadership

Interview type guidelines:
- technical: focus on job-specific skills, coding, problem-solving
- behavioral: focus on past experiences, soft skills, decision-making
- mixed: balanced mix of both

Generate questions that are relevant, non-trivial, and appropriate for the specified level. Do not reuse common interview questions unless specifically appropriate. Each question should be unique.
"""
    
    def _get_question_count(self, interview_type: str) -> int:
        """Get the number of questions for each interview type."""
        counts = {
            "technical": 5,
            "behavioral": 5,
            "mixed": 7,
        }
        return counts.get(interview_type, 5)
    
    def generate_questions(self, interview_type: str, target_role: str, 
                         difficulty: str, experience_level: str,
                         job_description: str = "", resume_context: str = "") -> List[Dict[str, Any]]:
        """Generate interview questions based on parameters."""
        prompt = self._build_question_prompt(
            interview_type, target_role, difficulty, experience_level,
            job_description, resume_context
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse the JSON array
            questions = json.loads(response.text.strip())
            
            if not isinstance(questions, list):
                raise ValueError("Expected a JSON array of questions")
            
            # Validate each question has required fields
            for q in questions:
                if not isinstance(q, dict):
                    continue
                if "question_text" not in q:
                    raise ValueError("Question missing required field: question_text")
                if "question_type" not in q:
                    q["question_type"] = "technical"
                if "expected_topics" not in q:
                    q["expected_topics"] = []
                if "difficulty" not in q:
                    q["difficulty"] = difficulty
            
            logger.info(f"Generated {len(questions)} interview questions")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini question response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            raise
    
    def _build_evaluation_prompt(self, question: str, question_type: str, 
                                expected_topics: List[str], answer: str,
                                difficulty: str, target_role: str) -> str:
        """Build a prompt for evaluating an interview answer."""
        topics_str = ", ".join(expected_topics) if expected_topics else "relevant concepts"
        
        return f"""
You are an expert interviewer evaluating a candidate's answer to a {question_type} question.

Question: {question}
Question type: {question_type}
Expected topics: {topics_str}
Candidate's difficulty level: {difficulty}
Target role: {target_role}

Candidate's answer:
---BEGIN ANSWER---
{answer}
---END ANSWER---

Evaluate the answer on these criteria (score 1-10 for each, or null if not applicable):
1. relevance: How well does the answer address the question?
2. technical_accuracy: For technical questions, how accurate is the technical content?
3. completeness: Does the answer cover all aspects of the question?
4. communication_quality: How clear, structured, and easy to understand is the answer?

Provide your evaluation in JSON format with exactly these keys:
{{
  "relevance_score": integer (1-10) or null,
  "technical_accuracy_score": integer (1-10) or null,
  "communication_score": integer (1-10) or null,
  "completeness_score": integer (1-10) or null,
  "feedback": "string (constructive feedback on the answer)",
  "suggested_answer": "string (a stronger, more complete answer to the question)",
  "evaluation_json": object with additional details
}}

Guidelines:
- Scores should be integers 1-10, or null if the criterion doesn't apply
- feedback should be specific, constructive, and actionable
- suggested_answer should be a strong, complete answer that addresses the question
- Do not fabricate information or make up technical details
- Consider the candidate's experience level when evaluating
- relevance and communication quality are always applicable
- technical_accuracy_score can be null for non-technical questions
- completeness_score should evaluate if all parts of the question were addressed

Be fair, accurate, and constructive. The goal is to help the candidate improve, not to criticize.
"""
    
    def evaluate_answer(self, question: str, question_type: str, 
                        expected_topics: List[str], answer: str,
                        difficulty: str, target_role: str) -> Dict[str, Any]:
        """Evaluate an interview answer and return structured feedback."""
        if not answer or not answer.strip():
            raise ValueError("Answer text is empty or contains only whitespace")
        
        if not question or not question.strip():
            raise ValueError("Question text is empty or contains only whitespace")
        
        try:
            prompt = self._build_evaluation_prompt(
                question, question_type, expected_topics, answer, difficulty, target_role
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse the JSON response
            result = json.loads(response.text.strip())
            
            # Validate required fields
            required_fields = ["relevance_score", "technical_accuracy_score", 
                             "communication_score", "completeness_score", 
                             "feedback", "suggested_answer", "evaluation_json"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure scores are valid or null
            for score_field in ["relevance_score", "technical_accuracy_score", 
                              "communication_score", "completeness_score"]:
                if result[score_field] is not None:
                    if not isinstance(result[score_field], int) or result[score_field] < 1 or result[score_field] > 10:
                        result[score_field] = None  # Reset invalid scores
            
            # Ensure feedback is a string
            if not isinstance(result["feedback"], str) or not result["feedback"].strip():
                result["feedback"] = "No feedback provided"
            
            # Ensure suggested_answer is a string
            if not isinstance(result["suggested_answer"], str) or not result["suggested_answer"].strip():
                result["suggested_answer"] = "No suggested answer available"
            
            # Ensure evaluation_json is an object
            if not isinstance(result["evaluation_json"], dict):
                result["evaluation_json"] = {}
            
            logger.info(f"Answer evaluated successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini evaluation response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Answer evaluation failed: {e}")
            raise
    
    def _build_report_prompt(self, interview_type: str, target_role: str,
                            difficulty: str, experience_level: str,
                            questions: List[Dict], answers: List[str],
                            scores: List[Dict], summary: str = "") -> str:
        """Build a prompt for generating the final interview report."""
        total_questions = len(questions)
        
        # Calculate averages
        scores_array = [s for s in scores if s is not None]
        avg_score = sum(s.get("relevance_score", 0) or 0 for s in scores_array) / len(scores_array) if scores_array else 0
        
        return f"""
You are generating a comprehensive interview report for a {interview_type} interview 
for a {target_role} position.

Interview summary:
- Interview type: {interview_type}
- Target role: {target_role}
- Difficulty: {difficulty}
- Experience level: {experience_level}
- Total questions: {total_questions}
- Average score: {avg_score:.1f}/10
- {summary if summary else ''}

Questions asked:
"""
        for i, (q, a, s) in enumerate(zip(questions, answers, scores), 1):
            score_info = ""
            if s:
                score_info = f"Scores - relevance: {s.get('relevance_score', 'N/A')}, " \
                           f"technical: {s.get('technical_accuracy_score', 'N/A')}, " \
                           f"communication: {s.get('communication_score', 'N/A')}, " \
                           f"completeness: {s.get('completeness_score', 'N/A')}"
            
            q_type = q.get("question_type", "technical")
            q_text = q.get("question_text", "Unknown question")
            
            self_content = f"""
Question {i} ({q_type}):
  Text: {q_text}
  Your answer: {a}
  {score_info}
"""
        
        return f"""
{self_content}

Overall interview analysis:
- Provide a comprehensive summary of the candidate's performance
- Identify key strengths and areas for improvement
- Suggest specific preparation topics and skills to focus on
- Provide an overall assessment with approximate strengths rating and growth areas
- Keep it professional, constructive, and actionable

Format the output as JSON with exactly these keys:
{{
  "overall_score": float (1-10, weighted average of all scores),
  "strengths": array of strings,
  "areas_for_improvement": array of strings,
  "preparation_topics": array of strings,
  "category_breakdown": object with score averages by category,
  "final_recommendations": array of strings,
  "report_json": object with additional details
}}
"""
    
    def generate_report(self, interview_type: str, target_role: str,
                       difficulty: str, experience_level: str,
                       questions: List[Dict], answers: List[str],
                       scores: List[Dict], summary: str = "") -> Dict[str, Any]:
        """Generate the final interview report."""
        if len(questions) != len(answers) or len(questions) != len(scores):
            raise ValueError("Questions, answers, and scores arrays must have the same length")
        
        if not questions:
            raise ValueError("At least one question is required")
        
        prompt = self._build_report_prompt(
            interview_type, target_role, difficulty, experience_level,
            questions, answers, scores, summary
        )
        
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
            required_fields = ["overall_score", "strengths", "areas_for_improvement",
                             "preparation_topics", "category_breakdown", 
                             "final_recommendations", "report_json"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure overall_score is a float 1-10
            if not isinstance(result["overall_score"], (int, float)) or result["overall_score"] < 1 or result["overall_score"] > 10:
                result["overall_score"] = 5.0
            
            # Ensure arrays are actually arrays
            for field in ["strengths", "areas_for_improvement", "preparation_topics", "final_recommendations"]:
                if not isinstance(result[field], list):
                    result[field] = []
            
            # Ensure category_breakdown is an object
            if not isinstance(result["category_breakdown"], dict):
                result["category_breakdown"] = {}
            
            # Ensure report_json is an object
            if not isinstance(result["report_json"], dict):
                result["report_json"] = {}
            
            logger.info(f"Interview report generated successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini report response as JSON: {e}")
            logger.error(f"Raw response: {response.text if response else 'None'}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise