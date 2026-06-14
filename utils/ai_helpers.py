"""
CareerPilot AI — AI Helpers (compatibility shim)
Delegates to services/ai_provider.py so all modules keep working unchanged.
"""

from services.ai_provider import (
    analyze_resume,
    generate_study_plan,
    generate_roadmap,
    generate_interview_questions,
    evaluate_answer,
    get_llm_response,
)

__all__ = [
    "analyze_resume",
    "generate_study_plan",
    "generate_roadmap",
    "generate_interview_questions",
    "evaluate_answer",
    "get_llm_response",
]
