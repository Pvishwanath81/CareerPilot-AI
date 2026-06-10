"""
CareerPilot AI — PDF Generator
Generates professional PDF reports using reportlab.
All functions return bytes (via BytesIO) for use with st.download_button.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Flowable

# ── Brand colours ──────────────────────────────────────────────────────────────
BLUE = HexColor("#0066FF")
BLACK = HexColor("#000000")
WHITE = HexColor("#FFFFFF")
GREEN = HexColor("#00A651")
RED = HexColor("#FF3B30")
ORANGE = HexColor("#FF9500")
LIGHT_BLUE = HexColor("#F0F4FF")
GREY = HexColor("#F5F5F5")


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _base_doc(buffer, title: str):
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        title=title,
        author="CareerPilot AI — Team Trident",
    )


def _styles():
    s = getSampleStyleSheet()
    custom = {
        "Title": ParagraphStyle(
            "Title", fontName="Helvetica-Bold", fontSize=22,
            leading=28, textColor=BLACK, spaceAfter=4,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle", fontName="Helvetica", fontSize=11,
            textColor=HexColor("#555555"), spaceAfter=6,
        ),
        "SectionHeader": ParagraphStyle(
            "SectionHeader", fontName="Helvetica-Bold", fontSize=13,
            textColor=BLACK, spaceBefore=14, spaceAfter=6,
            borderPad=4,
        ),
        "Body": ParagraphStyle(
            "Body", fontName="Helvetica", fontSize=10,
            leading=15, textColor=BLACK, spaceAfter=4,
        ),
        "BulletItem": ParagraphStyle(
            "BulletItem", fontName="Helvetica", fontSize=10,
            leading=14, textColor=BLACK, leftIndent=12, spaceAfter=3,
            bulletIndent=0,
        ),
        "Small": ParagraphStyle(
            "Small", fontName="Helvetica", fontSize=8,
            textColor=HexColor("#777777"),
        ),
        "Score": ParagraphStyle(
            "Score", fontName="Helvetica-Bold", fontSize=28,
            textColor=WHITE, alignment=TA_CENTER,
        ),
        "ScoreLabel": ParagraphStyle(
            "ScoreLabel", fontName="Helvetica-Bold", fontSize=9,
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=0,
        ),
        "Center": ParagraphStyle(
            "Center", fontName="Helvetica", fontSize=10,
            leading=14, textColor=BLACK, alignment=TA_CENTER,
        ),
        "CenterBold": ParagraphStyle(
            "CenterBold", fontName="Helvetica-Bold", fontSize=10,
            leading=14, textColor=BLACK, alignment=TA_CENTER,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader", fontName="Helvetica-Bold", fontSize=9,
            textColor=WHITE, alignment=TA_CENTER,
        ),
        "TableCell": ParagraphStyle(
            "TableCell", fontName="Helvetica", fontSize=9,
            textColor=BLACK,
        ),
    }
    return custom


def _header_footer(canvas, doc):
    """Draw branded header and footer on every page."""
    canvas.saveState()
    w, h = A4

    # Top blue bar
    canvas.setFillColor(BLUE)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(20 * mm, h - 9 * mm, "CareerPilot AI")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - 20 * mm, h - 9 * mm, f"Generated: {datetime.now().strftime('%d %b %Y')}")

    # Bottom footer
    canvas.setFillColor(BLACK)
    canvas.rect(0, 0, w, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(20 * mm, 3.5 * mm, "Built by Team Trident | CareerPilot AI")
    canvas.drawRightString(w - 20 * mm, 3.5 * mm, f"Page {doc.page}")

    canvas.restoreState()


def _score_table(scores: list) -> Table:
    """Create a row of coloured score badges. scores = [(label, value, color), ...]"""
    styles = _get_table_styles()
    data = []
    row_labels = []
    row_values = []
    for label, value, color in scores:
        row_values.append(Paragraph(str(value), ParagraphStyle(
            "Sc", fontName="Helvetica-Bold", fontSize=24, textColor=WHITE, alignment=TA_CENTER
        )))
        row_labels.append(Paragraph(label, ParagraphStyle(
            "Sl", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER
        )))
    data = [row_values, row_labels]
    col_w = 160 / len(scores) * mm
    t = Table(data, colWidths=[col_w] * len(scores), rowHeights=[20 * mm, 8 * mm])
    ts = [
        ("BACKGROUND", (0, 0), (-1, -1), BLUE),
        ("GRID", (0, 0), (-1, -1), 1, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]
    for i, (label, value, color) in enumerate(scores):
        ts.append(("BACKGROUND", (i, 0), (i, -1), color))
    t.setStyle(TableStyle(ts))
    return t


def _get_table_styles():
    return None  # placeholder


def _section_title(text: str, st: dict) -> list:
    """Return [HRFlowable, Paragraph] for a section heading."""
    return [
        HRFlowable(width="100%", thickness=2, color=BLACK, spaceAfter=4),
        Paragraph(f"▌ {text}", st["SectionHeader"]),
    ]


def _bullet_list(items: list, st: dict) -> list:
    """Convert a list of strings to bullet Paragraphs."""
    return [Paragraph(f"• {item}", st["BulletItem"]) for item in items if item]


# ── Resume Report ──────────────────────────────────────────────────────────────

def generate_resume_report(analysis_data: dict) -> bytes:
    """Generate a resume analysis PDF. Returns bytes."""
    buffer = io.BytesIO()
    doc = _base_doc(buffer, "Resume Analysis Report")
    st = _styles()
    story = []

    # Title
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Resume Analysis Report", st["Title"]))
    story.append(Paragraph(
        f"Experience Level: {analysis_data.get('experience_level', 'N/A')} | "
        f"Analysed: {datetime.now().strftime('%d %B %Y')}",
        st["Subtitle"]
    ))
    story.append(Spacer(1, 4 * mm))

    # Scores
    resume_score = analysis_data.get("resume_score", 0)
    ats_score = analysis_data.get("ats_score", 0)
    score_color = GREEN if resume_score >= 70 else (ORANGE if resume_score >= 50 else RED)
    ats_color = GREEN if ats_score >= 70 else (ORANGE if ats_score >= 50 else RED)
    story.append(_score_table([
        ("RESUME SCORE", f"{resume_score}/100", score_color),
        ("ATS SCORE", f"{ats_score}/100", ats_color),
    ]))
    story.append(Spacer(1, 6 * mm))

    # Strengths
    story += _section_title("Strengths", st)
    story += _bullet_list(analysis_data.get("strengths", []), st)
    story.append(Spacer(1, 3 * mm))

    # Weaknesses
    story += _section_title("Areas for Improvement", st)
    story += _bullet_list(analysis_data.get("weaknesses", []), st)
    story.append(Spacer(1, 3 * mm))

    # Skills Found
    skills_found = analysis_data.get("skills_found", [])
    story += _section_title("Skills Detected", st)
    if skills_found:
        chips_text = "  |  ".join(skills_found)
        story.append(Paragraph(chips_text, st["Body"]))
    story.append(Spacer(1, 3 * mm))

    # Missing Skills
    missing_skills = analysis_data.get("missing_skills", [])
    story += _section_title("Missing / Recommended Skills", st)
    story += _bullet_list(missing_skills, st)
    story.append(Spacer(1, 3 * mm))

    # Recommendations
    story += _section_title("AI Recommendations", st)
    for i, rec in enumerate(analysis_data.get("recommendations", []), 1):
        story.append(Paragraph(f"{i}. {rec}", st["BulletItem"]))
    story.append(Spacer(1, 6 * mm))

    # Skills table
    if skills_found or missing_skills:
        story += _section_title("Skills Summary Table", st)
        table_data = [
            [Paragraph("Skills Found", st["TableHeader"]), Paragraph("Missing Skills", st["TableHeader"])]
        ]
        max_rows = max(len(skills_found), len(missing_skills))
        for i in range(max_rows):
            f = skills_found[i] if i < len(skills_found) else ""
            m = missing_skills[i] if i < len(missing_skills) else ""
            table_data.append([Paragraph(f, st["TableCell"]), Paragraph(m, st["TableCell"])])
        t = Table(table_data, colWidths=[85 * mm, 85 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BLACK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()


# ── Study Plan Report ──────────────────────────────────────────────────────────

def generate_study_plan_report(plan_data: dict) -> bytes:
    """Generate a study plan PDF. Returns bytes."""
    buffer = io.BytesIO()
    doc = _base_doc(buffer, "Study Plan Report")
    st = _styles()
    story = []

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Personalised Study Plan", st["Title"]))
    story.append(Paragraph(
        f"Student: {plan_data.get('student_name', 'N/A')} | "
        f"Generated: {datetime.now().strftime('%d %B %Y')}",
        st["Subtitle"]
    ))
    story.append(Spacer(1, 4 * mm))

    # Priority Ranking
    priority = plan_data.get("priority_ranking", [])
    if priority:
        story += _section_title("Subject Priority Ranking", st)
        table_data = [[
            Paragraph("Subject", st["TableHeader"]),
            Paragraph("Priority", st["TableHeader"]),
            Paragraph("Reason", st["TableHeader"]),
        ]]
        for item in priority:
            color_map = {"High": RED, "Medium": ORANGE, "Low": GREEN}
            priority_label = item.get("priority", "Medium")
            bg = color_map.get(priority_label, BLUE)
            table_data.append([
                Paragraph(item.get("subject", ""), st["TableCell"]),
                Paragraph(priority_label, ParagraphStyle("P", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, alignment=TA_CENTER)),
                Paragraph(item.get("reason", ""), st["TableCell"]),
            ])
        t = Table(table_data, colWidths=[55 * mm, 30 * mm, 85 * mm])
        row_styles = [
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BLACK),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        for i, item in enumerate(priority, 1):
            priority_label = item.get("priority", "Medium")
            color_map = {"High": RED, "Medium": ORANGE, "Low": GREEN}
            row_styles.append(("BACKGROUND", (1, i), (1, i), color_map.get(priority_label, BLUE)))
        t.setStyle(TableStyle(row_styles))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    # Daily Schedule
    daily = plan_data.get("daily_schedule", [])
    if daily:
        story += _section_title("Daily Study Schedule", st)
        table_data = [[
            Paragraph("Day", st["TableHeader"]),
            Paragraph("Subject", st["TableHeader"]),
            Paragraph("Hours", st["TableHeader"]),
            Paragraph("Topics", st["TableHeader"]),
        ]]
        for entry in daily:
            table_data.append([
                Paragraph(str(entry.get("day", "")), st["TableCell"]),
                Paragraph(str(entry.get("subject", "")), st["TableCell"]),
                Paragraph(str(entry.get("hours", "")), st["TableCell"]),
                Paragraph(str(entry.get("topics", "")), st["TableCell"]),
            ])
        t = Table(table_data, colWidths=[30 * mm, 45 * mm, 20 * mm, 75 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BLACK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    # Weekly Plan
    weekly = plan_data.get("weekly_plan", [])
    if weekly:
        story += _section_title("Weekly Plan Overview", st)
        for week in weekly:
            subjects = ", ".join(week.get("subjects", []))
            story.append(Paragraph(
                f"<b>Week {week.get('week', '?')} — {week.get('focus', '')}</b>",
                st["SectionHeader"]
            ))
            story.append(Paragraph(f"Subjects: {subjects}", st["Body"]))
            story.append(Paragraph(f"Goals: {week.get('goals', '')}", st["Body"]))
            story.append(Spacer(1, 3 * mm))

    # Tips
    tips = plan_data.get("tips", [])
    if tips:
        story += _section_title("Study Tips", st)
        story += _bullet_list(tips, st)

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()


# ── Roadmap Report ─────────────────────────────────────────────────────────────

def generate_roadmap_report(roadmap_data: dict) -> bytes:
    """Generate a career roadmap PDF. Returns bytes."""
    buffer = io.BytesIO()
    doc = _base_doc(buffer, "Career Roadmap")
    st = _styles()
    story = []

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Career Roadmap", st["Title"]))
    story.append(Paragraph(
        f"Goal: {roadmap_data.get('career_goal', 'N/A')} | "
        f"Level: {roadmap_data.get('experience_level', 'N/A')} | "
        f"Generated: {datetime.now().strftime('%d %B %Y')}",
        st["Subtitle"]
    ))
    story.append(Spacer(1, 4 * mm))

    roadmap = roadmap_data.get("roadmap_data", {})
    months = roadmap.get("roadmap", []) if isinstance(roadmap, dict) else []

    for m in months:
        story.append(KeepTogether([
            HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=3),
            Paragraph(f"Month {m.get('month', '?')} — {m.get('title', '')}", st["SectionHeader"]),
        ]))

        skills = m.get("skills_to_learn", [])
        if skills:
            story.append(Paragraph("<b>Skills to Learn:</b>", st["Body"]))
            story += _bullet_list(skills, st)

        projects = m.get("projects_to_build", [])
        if projects:
            story.append(Paragraph("<b>Projects to Build:</b>", st["Body"]))
            story += _bullet_list(projects, st)

        courses = m.get("courses", [])
        if courses:
            story.append(Paragraph("<b>Courses:</b>", st["Body"]))
            story += _bullet_list(courses, st)

        certs = m.get("certifications", [])
        if certs:
            story.append(Paragraph("<b>Certifications:</b>", st["Body"]))
            story += _bullet_list(certs, st)

        milestone = m.get("milestones", "")
        if milestone:
            story.append(Paragraph(f"🏆 <b>Milestone:</b> {milestone}", st["Body"]))

        story.append(Spacer(1, 5 * mm))

    # Job Prep
    job_prep = roadmap.get("job_prep", {}) if isinstance(roadmap, dict) else {}
    if job_prep:
        story += _section_title("Job Preparation", st)
        if job_prep.get("resume_tips"):
            story.append(Paragraph("<b>Resume Tips:</b>", st["Body"]))
            story += _bullet_list(job_prep["resume_tips"], st)
        if job_prep.get("interview_topics"):
            story.append(Paragraph("<b>Interview Topics:</b>", st["Body"]))
            story += _bullet_list(job_prep["interview_topics"], st)
        if job_prep.get("platforms"):
            story.append(Paragraph(
                "<b>Platforms:</b> " + ", ".join(job_prep["platforms"]), st["Body"]
            ))

    # Resources
    resources = roadmap.get("resources", []) if isinstance(roadmap, dict) else []
    if resources:
        story += _section_title("Learning Resources", st)
        table_data = [[
            Paragraph("Resource", st["TableHeader"]),
            Paragraph("Type", st["TableHeader"]),
            Paragraph("URL", st["TableHeader"]),
            Paragraph("Free?", st["TableHeader"]),
        ]]
        for r in resources:
            table_data.append([
                Paragraph(r.get("name", ""), st["TableCell"]),
                Paragraph(r.get("type", ""), st["TableCell"]),
                Paragraph(r.get("url", ""), st["TableCell"]),
                Paragraph("✅ Free" if r.get("free") else "💰 Paid", st["TableCell"]),
            ])
        t = Table(table_data, colWidths=[45 * mm, 25 * mm, 75 * mm, 25 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BLACK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()


# ── Interview Report ───────────────────────────────────────────────────────────

def generate_interview_report(session_data: dict) -> bytes:
    """Generate an interview session PDF. Returns bytes."""
    buffer = io.BytesIO()
    doc = _base_doc(buffer, "Interview Session Report")
    st = _styles()
    story = []

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Interview Session Report", st["Title"]))

    total = session_data.get("total_score", 0)
    max_s = session_data.get("max_score", 100)
    grade = session_data.get("grade", "N/A")
    story.append(Paragraph(
        f"Role: {session_data.get('role', 'N/A')} | "
        f"Difficulty: {session_data.get('difficulty', 'N/A')} | "
        f"Date: {datetime.now().strftime('%d %B %Y')}",
        st["Subtitle"]
    ))
    story.append(Spacer(1, 4 * mm))

    # Score summary
    pct = int((total / max_s) * 100) if max_s else 0
    score_color = GREEN if pct >= 70 else (ORANGE if pct >= 50 else RED)
    story.append(_score_table([
        ("TOTAL SCORE", f"{total}/{max_s}", score_color),
        ("PERCENTAGE", f"{pct}%", score_color),
        ("GRADE", grade, BLUE),
    ]))
    story.append(Spacer(1, 6 * mm))

    # Q&A
    questions_data = session_data.get("questions_data", [])
    if questions_data:
        story += _section_title("Question-by-Question Breakdown", st)
        for i, qa in enumerate(questions_data, 1):
            score = qa.get("score", 0)
            q_color = GREEN if score >= 7 else (ORANGE if score >= 5 else RED)
            story.append(KeepTogether([
                Paragraph(
                    f"<b>Q{i}. {qa.get('question', '')}</b>",
                    ParagraphStyle("QH", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK, spaceBefore=8, spaceAfter=3)
                ),
                Paragraph(f"<b>Your Answer:</b> {qa.get('user_answer', 'Not answered')}", st["Body"]),
                Paragraph(f"<b>Score:</b> {score}/10", st["Body"]),
                Paragraph(f"<b>Feedback:</b> {qa.get('feedback', '')}", st["Body"]),
                Paragraph(f"<b>Model Answer:</b> {qa.get('model_answer', '')}", st["Body"]),
            ]))

            missed = qa.get("key_points_missed", [])
            if missed:
                story.append(Paragraph("<b>Key Points Missed:</b>", st["Body"]))
                story += _bullet_list(missed, st)
            story.append(Spacer(1, 3 * mm))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()
