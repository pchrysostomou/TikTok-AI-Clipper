from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import process, auth, clips
import cloudinary
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

app = FastAPI(title="YouTube → TikTok AI Clipper", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev: open for all. Restrict to FRONTEND_URL in production.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(clips.router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "message": "YouTube → TikTok AI Clipper API 🚀"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
