from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import SpeakerRequest, SpeakerResponse
from services.claude import get_speaker_profile, extract_profile_from_resume
import pypdf
import io

# APIRouter is like a mini FastAPI app
# We use it to group related endpoints together
# Then we'll plug this router into the main app
router = APIRouter()

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
        return profile

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting resume: {str(e)}"
        )