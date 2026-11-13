import os

from fastapi import APIRouter, FastAPI, HTTPException
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

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "ai": bool(os.getenv("ANTHROPIC_API_KEY"))}


@router.post("/storyboard", response_model=Storyboard)
def storyboard(req: StoryboardRequest):
    try:
        return generate_storyboard(req)
    except Exception as exc:  # surface a clean error to the UI
        raise HTTPException(status_code=502, detail=f"Storyboard generation failed: {exc}")


@router.post("/scene/regenerate", response_model=Scene)
def regenerate(body: RegenerateRequest):
    try:
        return regenerate_scene(body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scene regeneration failed: {exc}")


# Serverless hosts differ in whether the "/api" prefix (or the "/api/index"
# function name) reaches the app, so expose the same routes under each form.
# The frontend always calls /api/*.
for prefix in ("/api", "/api/index", ""):
    app.include_router(router, prefix=prefix, include_in_schema=(prefix == "/api"))


@app.get("/", include_in_schema=False)
def root():
    return {"service": "CineFlow AI", "health": "/api/health", "docs": "/docs"}
