from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from models.schemas import SpeakerRequest, SpeakerResponse
from services.claude import (
    get_speaker_profile,
    extract_profile_from_resume,
    generate_portfolio_html,
)
import pypdf
import io
import uuid
import os
import re

# APIRouter is like a mini FastAPI app
# We use it to group related endpoints together
# Then we'll plug this router into the main app
router = APIRouter()

PORTFOLIO_DIR = "portfolios"
RESUME_DIR = "resumes"
os.makedirs(PORTFOLIO_DIR, exist_ok=True)
os.makedirs(RESUME_DIR, exist_ok=True)


def _safe_storage_id(file_id: str) -> str:
    if not re.fullmatch(r"[a-f0-9]{8}", file_id):
        raise HTTPException(status_code=404, detail="Not found")
    return file_id

@router.post("/research", response_model=SpeakerResponse)
async def research_speaker(request: SpeakerRequest):
    """
    POST /api/research
    Receives: { "name": "Andrej Karpathy" }
    Returns: full speaker profile with questions and intro line
    """
    
    try:
        # Call our claude service with the speaker name
        profile = get_speaker_profile(request.name, request.user_background)
        
        # Return it as a SpeakerResponse
        # FastAPI automatically validates it matches the schema
        return profile
        
    except Exception as e:
        # If anything goes wrong, return a proper HTTP error
        # 500 = Internal Server Error
        raise HTTPException(
            status_code=500,
            detail=f"Error researching speaker: {str(e)}"
        )


@router.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):
    """
    POST /api/extract-resume
    Accepts a PDF file upload, extracts text, and returns structured profile data.
    """
    try:
        contents = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()

        profile = extract_profile_from_resume(resume_text)
        resume_id = str(uuid.uuid4())[:8]
        with open(f"{RESUME_DIR}/{resume_id}.pdf", "wb") as f:
            f.write(contents)
        profile["resume_id"] = resume_id
        return profile

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting resume: {str(e)}"
        )


@router.post("/generate-portfolio")
async def generate_portfolio(body: dict):
    """
    POST /api/generate-portfolio
    Takes extracted profile data, optional theme and font, generates portfolio HTML, returns portfolio_id.
    """
    try:
        theme = body.get("theme")
        font = body.get("font")
        profile = {k: v for k, v in body.items() if k not in ("theme", "font")}
        html = generate_portfolio_html(profile, theme=theme, font=font)
        portfolio_id = str(uuid.uuid4())[:8]
        with open(f"{PORTFOLIO_DIR}/{portfolio_id}.html", "w") as f:
            f.write(html)
        return {"portfolio_id": portfolio_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating portfolio: {str(e)}")


@router.get("/portfolio/{portfolio_id}", response_class=HTMLResponse)
async def get_portfolio(portfolio_id: str):
    """
    GET /api/portfolio/{portfolio_id}
    Serves the generated portfolio HTML page directly.
    """
    try:
        _safe_storage_id(portfolio_id)
        with open(f"{PORTFOLIO_DIR}/{portfolio_id}.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio not found")


@router.get("/resume/{resume_id}")
async def get_resume(resume_id: str):
    """
    GET /api/resume/{resume_id}
    Serves the uploaded resume PDF for download.
    """
    _safe_storage_id(resume_id)
    path = f"{RESUME_DIR}/{resume_id}.pdf"
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Resume not found")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="resume.pdf",
        headers={"Content-Disposition": 'attachment; filename="resume.pdf"'},
    )