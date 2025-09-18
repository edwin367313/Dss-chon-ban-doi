from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.Core import Config
from backend.app.routers import auth, candidates, social, photos  # <- chỉ router SQL

app = FastAPI(title=Config.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static: /uploads
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Routers (KHÔNG include mock)
app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(social.router)
app.include_router(photos.router)

@app.get("/api/health")
def health():
    return {"ok": True}
