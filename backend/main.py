"""
backend/main.py
FastAPI backend server for SkillSync AI.
Exposes endpoints for job roles, resume analysis, and AI assistant chat.
Serves the premium frontend SPA static assets.
"""
import sys
from pathlib import Path

# Add project root to path so we can import from 'modules' and 'database'
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skillsync-backend")

app = FastAPI(title="SkillSync AI Full-Stack Backend")

# Enable CORS for frontend local development (if any)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/job-roles")
def get_job_roles():
    """Load and return the list of available job roles."""
    csv_path = project_root / "data" / "raw" / "job_roles.csv"
    try:
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if "job_role" in df.columns:
                return {"job_roles": df["job_role"].dropna().unique().tolist()}
        # Fallback if file doesn't exist
        return {
            "job_roles": [
                "Data Scientist",
                "Software Engineer",
                "Data Analyst",
                "ML Engineer",
                "Web Developer",
                "DevOps Engineer",
                "NLP Engineer",
                "Business Analyst"
            ]
        }
    except Exception as e:
        logger.error(f"Error loading job roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_role: str = Form(...),
    jd_text: str = Form(""),
    use_semantic: bool = Form(True)
):
    """
    Run full resume parsing and analysis pipeline.
    Accepts multipart form upload.
    """
    try:
        logger.info(f"Received resume analysis request for role: {job_role}")
        file_bytes = await file.read()
        file_name = file.filename or ""
        file_type = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else "pdf"

        if file_type not in ("pdf", "docx", "doc"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_type}. Supported: pdf, docx, doc"
            )

        # Retrieve required skills from CSV for the job role to pass as fallback
        jd_skills = []
        csv_path = project_root / "data" / "raw" / "job_roles.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            row = df[df["job_role"].str.lower() == job_role.lower()]
            if not row.empty and "required_skills" in df.columns:
                skills_str = row.iloc[0]["required_skills"]
                if isinstance(skills_str, str):
                    jd_skills = [s.strip() for s in skills_str.split(",")]

        # Use fallback if jd_text is empty
        final_jd = jd_text if jd_text.strip() else " ".join(jd_skills)

        from modules.pipeline import run_analysis
        result = run_analysis(
            file_bytes=file_bytes,
            file_type=file_type,
            job_role=job_role,
            jd_text=final_jd,
            jd_skills=jd_skills,
            use_semantic=use_semantic,
            session_id="full_stack_session"
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        logger.exception("Error during resume analysis")
        raise HTTPException(status_code=500, detail=str(e))


class ChatMessage(BaseModel):
    message: str


@app.post("/api/chat")
def chat_with_assistant(payload: ChatMessage):
    """Chat with the Gemini integration career assistant."""
    try:
        from modules.llm_integration import GeminiIntegration
        gemini = GeminiIntegration()
        response_text = gemini.answer_question(payload.message)
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files to serve the SPA (must be mounted after API routes)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
