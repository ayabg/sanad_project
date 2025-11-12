from fastapi import FastAPI
from .api import chat

app = FastAPI(
    title="Sanad AI Backend",
    description="Secure API for Mental Health AI Companion",
)

# Prefix all API routes with /api/v1
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Sanad Backend is operational"}
