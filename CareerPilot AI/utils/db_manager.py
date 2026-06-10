"""
CareerPilot AI — Database Manager
Handles all SQLite operations for persistent storage.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "careerpilot.db")


def get_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize all database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resume_score INTEGER,
            ats_score INTEGER,
            strengths TEXT,
            weaknesses TEXT,
            missing_skills TEXT,
            recommendations TEXT,
            skills_found TEXT,
            experience_level TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            student_name TEXT,
            subjects TEXT,
            daily_schedule TEXT,
            weekly_plan TEXT,
            priority_ranking TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            career_goal TEXT,
            experience_level TEXT,
            roadmap_data TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            difficulty TEXT,
            total_score INTEGER,
            max_score INTEGER,
            grade TEXT,
            questions_data TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_resume_analysis(data: dict) -> int:
    """Save resume analysis results. Returns inserted row ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resume_analysis
            (resume_score, ats_score, strengths, weaknesses, missing_skills,
             recommendations, skills_found, experience_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("resume_score", 0),
        data.get("ats_score", 0),
        json.dumps(data.get("strengths", [])),
        json.dumps(data.get("weaknesses", [])),
        json.dumps(data.get("missing_skills", [])),
        json.dumps(data.get("recommendations", [])),
        json.dumps(data.get("skills_found", [])),
        data.get("experience_level", "Unknown"),
    ))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_study_plan(data: dict) -> int:
    """Save a generated study plan. Returns inserted row ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO study_plans
            (student_name, subjects, daily_schedule, weekly_plan, priority_ranking)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("student_name", ""),
        json.dumps(data.get("subjects", [])),
        json.dumps(data.get("daily_schedule", [])),
        json.dumps(data.get("weekly_plan", [])),
        json.dumps(data.get("priority_ranking", [])),
    ))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_career_roadmap(data: dict) -> int:
    """Save a generated career roadmap. Returns inserted row ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO career_roadmaps (career_goal, experience_level, roadmap_data)
        VALUES (?, ?, ?)
    """, (
        data.get("career_goal", ""),
        data.get("experience_level", ""),
        json.dumps(data.get("roadmap_data", {})),
    ))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_interview_session(data: dict) -> int:
    """Save an interview session. Returns inserted row ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interview_sessions
            (role, difficulty, total_score, max_score, grade, questions_data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("role", ""),
        data.get("difficulty", ""),
        data.get("total_score", 0),
        data.get("max_score", 100),
        data.get("grade", "N/A"),
        json.dumps(data.get("questions_data", [])),
    ))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_latest_analysis() -> dict | None:
    """Return the most recent resume analysis or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM resume_analysis ORDER BY date DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return _parse_resume_row(row)


def get_all_resume_analyses() -> list:
    """Return all resume analyses ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_analysis ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_parse_resume_row(r) for r in rows]


def get_all_study_plans() -> list:
    """Return all study plans ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_plans ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "date": r["date"],
            "student_name": r["student_name"],
            "subjects": _safe_json(r["subjects"]),
            "daily_schedule": _safe_json(r["daily_schedule"]),
            "weekly_plan": _safe_json(r["weekly_plan"]),
            "priority_ranking": _safe_json(r["priority_ranking"]),
        })
    return result


def get_all_roadmaps() -> list:
    """Return all roadmaps ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM career_roadmaps ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "date": r["date"],
            "career_goal": r["career_goal"],
            "experience_level": r["experience_level"],
            "roadmap_data": _safe_json(r["roadmap_data"]),
        })
    return result


def get_all_interview_sessions() -> list:
    """Return all interview sessions ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interview_sessions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "date": r["date"],
            "role": r["role"],
            "difficulty": r["difficulty"],
            "total_score": r["total_score"],
            "max_score": r["max_score"],
            "grade": r["grade"],
            "questions_data": _safe_json(r["questions_data"]),
        })
    return result


def delete_all_data():
    """Delete all records from all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    for table in ["resume_analysis", "study_plans", "career_roadmaps", "interview_sessions"]:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()


# ---- Private helpers ----

def _parse_resume_row(row) -> dict:
    return {
        "id": row["id"],
        "date": row["date"],
        "resume_score": row["resume_score"],
        "ats_score": row["ats_score"],
        "strengths": _safe_json(row["strengths"]),
        "weaknesses": _safe_json(row["weaknesses"]),
        "missing_skills": _safe_json(row["missing_skills"]),
        "recommendations": _safe_json(row["recommendations"]),
        "skills_found": _safe_json(row["skills_found"]),
        "experience_level": row["experience_level"],
    }


def _safe_json(value) -> list | dict:
    if value is None:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
