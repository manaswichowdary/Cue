from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.research import router as research_router

app = FastAPI(
    title="Speaker Prep API",
    description="AI-powered speaker research tool for ai.engineer conference",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "https://cue-sepia-omega.vercel.app",
    ],
    allow_origin_regex=r"http://localhost:\d+|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research_router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "running", "message": "Speaker Prep API is live"}