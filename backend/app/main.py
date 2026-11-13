import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .director import generate_storyboard, regenerate_scene
from .models import RegenerateRequest, Scene, Storyboard, StoryboardRequest

app = FastAPI(title="CineFlow AI", version="0.1.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX") or None,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "ai": bool(os.getenv("ANTHROPIC_API_KEY"))}


@app.post("/api/storyboard", response_model=Storyboard)
def storyboard(req: StoryboardRequest):
    try:
        return generate_storyboard(req)
    except Exception as exc:  # surface a clean error to the UI
        raise HTTPException(status_code=502, detail=f"Storyboard generation failed: {exc}")


@app.post("/api/scene/regenerate", response_model=Scene)
def regenerate(body: RegenerateRequest):
    try:
        return regenerate_scene(body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scene regeneration failed: {exc}")
