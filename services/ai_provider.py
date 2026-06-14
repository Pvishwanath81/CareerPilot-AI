"""
CareerPilot AI — Unified AI Provider
Supports BYOK (Gemini) and Ollama (Local) inference.
"""

import os as _os, sys as _sys
_mod_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_mod_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)


import os
import json
import re
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODELS = ["llama3", "mistral", "gemma"]
GEMINI_MODEL = "gemini-1.5-flash"


# ── Language instruction helpers ───────────────────────────────────────────────

def _language_instruction() -> str:
    """
    Return a language instruction string to prepend to every prompt,
    so the AI responds in the user's chosen language.
    """
    lang = st.session_state.get("language", "en")
    if lang == "te":
        return (
            "IMPORTANT: You must respond ONLY in Telugu (తెలుగు) language. "
            "All your text output — including keys' string values, feedback, "
            "recommendations, tips, and any other human-readable text — must be "
            "written in Telugu script. Do NOT use English for any human-readable "
            "content. JSON keys must remain in English exactly as specified.\n\n"
        )
    # Default: English
    return (
        "IMPORTANT: You must respond ONLY in English. "
        "All human-readable text in your JSON response must be in English.\n\n"
    )


# ── Provider helpers ───────────────────────────────────────────────────────────

def get_active_provider() -> str:
    return st.session_state.get("ai_provider", "BYOK")


def get_byok_api_key() -> str:
    """Return user-supplied key, falling back to .env."""
    user_key = st.session_state.get("byok_api_key", "").strip()
    if user_key:
        return user_key
    return os.getenv("GOOGLE_API_KEY", "").strip()


def get_ollama_model() -> str:
    return st.session_state.get("ollama_model", "llama3")


def check_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ── Core response function ─────────────────────────────────────────────────────

def get_llm_response(prompt: str) -> str:
    """
    Send a prompt to the active AI provider and return the raw text response.
    Prepends a language instruction so the model replies in the user's language.
    Raises ValueError / RuntimeError on configuration or connection problems.
    """
    lang_instruction = _language_instruction()
    full_prompt = lang_instruction + prompt

    provider = get_active_provider()
    if provider == "Ollama (Local)":
        return _call_ollama(full_prompt)
    else:
        return _call_gemini(full_prompt)


def _call_gemini(prompt: str) -> str:
    api_key = get_byok_api_key()
    if not api_key:
        raise ValueError(
            "No Gemini API key found. Please enter your key in the AI Settings sidebar."
        )
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")


def _call_ollama(prompt: str) -> str:
    model = get_ollama_model()
    if not check_ollama_running():
        raise RuntimeError(
            "Ollama is not running. Start it with: ollama serve"
        )
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Ollama. Make sure it is running: ollama serve")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")


# ── JSON helpers ───────────────────────────────────────────────────────────────

def _clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_response(response_text: str) -> dict:
    cleaned = _clean_json_response(response_text)
    return json.loads(cleaned)


# ── Domain-level AI calls (used by all modules) ────────────────────────────────

def analyze_resume(resume_text: str) -> dict:
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
    try:
        text = get_llm_response(prompt)
        return _parse_response(text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"AI analysis failed: {e}"}


def generate_study_plan(student_data: dict) -> dict:
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
    try:
        text = get_llm_response(prompt)
        return _parse_response(text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Study plan generation failed: {e}"}


def generate_roadmap(career_data: dict) -> dict:
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
    try:
        text = get_llm_response(prompt)
        return _parse_response(text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Roadmap generation failed: {e}"}


def generate_interview_questions(role: str, difficulty: str, q_type: str) -> dict:
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
    try:
        text = get_llm_response(prompt)
        return _parse_response(text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Question generation failed: {e}"}


def evaluate_answer(question: str, answer: str, role: str) -> dict:
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
    try:
        text = get_llm_response(prompt)
        return _parse_response(text)
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": f"Answer evaluation failed: {e}"}
