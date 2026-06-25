from pydantic import BaseModel
from typing import List

class SpeakerRequest(BaseModel):
    name: str
    user_background: str = ""

class SpeakerResponse(BaseModel):
    name: str
    role: str
    company: str
    why_they_matter: str
    questions: List[str]
    intro_line: str
    found: bool