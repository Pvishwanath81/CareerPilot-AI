# CareerPilot AI

## Overview

CareerPilot AI is an AI-powered Career and Academic Success Platform designed for students. It helps users analyze resumes, generate study plans, track career readiness, create career roadmaps, and practice interviews using Google Gemini AI.

## Features

### AI Resume Analyzer

* Upload PDF resumes
* Resume score calculation
* ATS score analysis
* Skill gap detection
* AI recommendations

### Smart Study Planner

* Personalized study schedules
* Subject prioritization
* Revision planning
* Daily and weekly plans

### Career Readiness Dashboard

* Resume score tracking
* ATS score tracking
* Skill coverage analytics
* Career readiness percentage

### Career Roadmap Generator

* Role-based learning roadmap
* Monthly milestones
* Recommended projects
* Certification suggestions

### AI Interview Coach

* AI-generated interview questions
* Answer evaluation
* Feedback and scoring
* Session summaries

### Reports

* Download PDF reports
* Resume reports
* Study plans
* Career roadmaps
* Interview summaries

---

## Tech Stack

* Streamlit
* Python
* Google Gemini API
* SQLite
* Plotly
* ReportLab
* PyPDF2
* Pandas

---

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd CareerPilot-AI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```text
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## Run the Application

```bash
streamlit run app.py
```

Application will open at:

```text
http://localhost:8501
```

---

## Project Structure

```text
CareerPilot-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── modules/
│   ├── resume_analyzer.py
│   ├── study_planner.py
│   ├── career_dashboard.py
│   ├── roadmap_generator.py
│   ├── interview_coach.py
│   └── reports.py
│
├── utils/
│   ├── ai_helpers.py
│   ├── db_manager.py
│   └── pdf_generator.py
│
├── assets/
│   └── style.css
│
└── database/
```

---

## Deployment

### Streamlit Cloud

1. Push project to GitHub.
2. Login to Streamlit Cloud.
3. Create a new application.
4. Select repository.
5. Set `app.py` as the main file.
6. Add the secret:

```text
GOOGLE_API_KEY=your_gemini_api_key_here
```

7. Deploy.

---

## Team

* P. Vishwanath
* D. Sathvik

Hackathon Project
