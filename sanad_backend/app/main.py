from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat

app = FastAPI(
    title="Sanad AI Backend",
    description="Secure API for Mental Health AI Companion",
)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefix all API routes with /api/v1
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Sanad Backend is operational"}
