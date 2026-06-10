"""
CareerPilot AI — AI Helpers
All Google Gemini API calls are centralised here.
"""

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GOOGLE_API_KEY", "")
if _api_key:
    genai.configure(api_key=_api_key)

MODEL_NAME = "gemini-1.5-flash"


def _get_model():
    """Return a configured GenerativeModel instance."""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences and extra whitespace from model output."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_response(response_text: str) -> dict:
    """Parse cleaned JSON from model response text."""
    cleaned = _clean_json_response(response_text)
    return json.loads(cleaned)


# ──────────────────────────────────────────────────────────────────────────────
# Resume Analyzer
# ──────────────────────────────────────────────────────────────────────────────

def analyze_resume(resume_text: str) -> dict:
    """
    Analyse a resume and return structured feedback as a dict.
    Returns {'error': str} on failure.
    """
    try:
        model = _get_model()
        prompt = f"""You are an expert resume reviewer and ATS specialist.
Analyze this resume text and return ONLY a valid JSON object with exactly these keys (no extra text, no markdown):
{{
  "resume_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "missing_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "recommendations": ["rec1", "rec2", "rec3", "rec4", "rec5"],
  "skills_found": ["skill1", "skill2"],
  "experience_level": "Fresher"
}}
experience_level must be one of: Fresher, Junior, Mid-Level, Senior.
Provide 3-5 items for strengths/weaknesses, 5-8 for missing_skills, exactly 5 recommendations.

Resume text:
{resume_text[:8000]}"""

        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"AI analysis failed: {e}"}


# ──────────────────────────────────────────────────────────────────────────────
# Study Planner
# ──────────────────────────────────────────────────────────────────────────────

def generate_study_plan(student_data: dict) -> dict:
    """
    Generate a personalised study plan.
    Returns {'error': str} on failure.
    """
    try:
        model = _get_model()
        prompt = f"""You are an expert academic planner.
Generate a detailed study plan and return ONLY valid JSON (no extra text, no markdown):
{{
  "daily_schedule": [
    {{"day": "Monday", "subject": "Mathematics", "hours": 2.0, "topics": "Calculus Chapter 3"}}
  ],
  "weekly_plan": [
    {{"week": 1, "focus": "Foundation", "subjects": ["Math", "Physics"], "goals": "Complete chapters 1-3"}}
  ],
  "priority_ranking": [
    {{"subject": "Mathematics", "priority": "High", "reason": "Exam in 2 weeks"}}
  ],
  "revision_plan": [
    {{"subject": "Mathematics", "revision_date": "2024-01-15", "strategy": "Practice problems"}}
  ],
  "tips": ["tip1", "tip2", "tip3", "tip4", "tip5"]
}}
Create at least 7 days in daily_schedule, at least 4 weeks in weekly_plan.
Exactly 5 tips.

Student data:
{json.dumps(student_data, indent=2)}"""

        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Study plan generation failed: {e}"}


# ──────────────────────────────────────────────────────────────────────────────
# Career Roadmap
# ──────────────────────────────────────────────────────────────────────────────

def generate_roadmap(career_data: dict) -> dict:
    """
    Generate a month-by-month career roadmap.
    Returns {'error': str} on failure.
    """
    try:
        model = _get_model()
        months = int(career_data.get("timeline_months", 6))
        prompt = f"""You are an expert career coach.
Generate a detailed career roadmap and return ONLY valid JSON (no extra text, no markdown):
{{
  "roadmap": [
    {{
      "month": 1,
      "title": "Foundation Building",
      "skills_to_learn": ["Python basics", "Data structures"],
      "projects_to_build": ["Calculator app", "To-do list"],
      "courses": ["CS50 on edX", "Python Crash Course"],
      "certifications": ["AWS Cloud Practitioner"],
      "milestones": "Complete 2 beginner projects"
    }}
  ],
  "job_prep": {{
    "resume_tips": ["tip1", "tip2"],
    "interview_topics": ["topic1", "topic2"],
    "platforms": ["LinkedIn", "LeetCode"]
  }},
  "resources": [
    {{"name": "freeCodeCamp", "type": "Website", "url": "https://freecodecamp.org", "free": true}}
  ]
}}
Generate exactly {months} month objects in the roadmap array.
At least 5 resources.

Career data:
{json.dumps(career_data, indent=2)}"""

        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Roadmap generation failed: {e}"}


# ──────────────────────────────────────────────────────────────────────────────
# Interview Coach
# ──────────────────────────────────────────────────────────────────────────────

def generate_interview_questions(role: str, difficulty: str, q_type: str) -> dict:
    """
    Generate 10 interview questions for a given role/difficulty/type.
    Returns {'error': str} on failure.
    """
    try:
        model = _get_model()
        prompt = f"""Generate exactly 10 interview questions for a {role} position at {difficulty} level.
Question type: {q_type}.
Return ONLY valid JSON (no extra text, no markdown):
{{
  "questions": [
    {{
      "id": 1,
      "question": "Explain the difference between a list and a tuple in Python.",
      "type": "Technical",
      "expected_keywords": ["immutable", "mutable", "performance", "hashable"]
    }}
  ]
}}
Ensure all 10 questions are relevant, varied, and appropriately difficult for {difficulty} level."""

        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Question generation failed: {e}"}


def evaluate_answer(question: str, answer: str, role: str) -> dict:
    """
    Evaluate a candidate's interview answer.
    Returns {'error': str} on failure.
    """
    try:
        model = _get_model()

        if not answer or not answer.strip():
            return {
                "score": 0,
                "feedback": "No answer was provided.",
                "model_answer": "Please provide an answer to receive evaluation.",
                "key_points_missed": ["No answer given"],
                "confidence_level": "Low",
            }

        prompt = f"""You are an expert technical interviewer for {role} positions.
Evaluate this interview answer and return ONLY valid JSON (no extra text, no markdown):
{{
  "score": <integer 0-10>,
  "feedback": "Detailed paragraph feedback on the answer quality.",
  "model_answer": "A comprehensive model answer that covers all key points.",
  "key_points_missed": ["point1", "point2"],
  "confidence_level": "Low"
}}
confidence_level must be one of: Low, Medium, High.
Be fair but thorough. Score 0-10 where 10 is perfect.

Question: {question}

Candidate's Answer: {answer}"""

        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Answer evaluation failed: {e}"}
