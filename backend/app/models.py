from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Genre = Literal["Action", "Horror", "Comedy", "Sci-Fi", "Romance", "Anime", "Documentary"]
Style = Literal["Hollywood cinematic", "Pixar-like animation", "Anime", "Realistic", "Dark horror", "Documentary"]
AspectRatio = Literal["9:16", "16:9"]


class StoryboardRequest(BaseModel):
    idea: str = Field(min_length=10, max_length=1000)
    genre: Genre = "Sci-Fi"
    length_seconds: int = Field(default=30, ge=10, le=120)
    style: Style = "Hollywood cinematic"
    aspect_ratio: AspectRatio = "16:9"


class Scene(BaseModel):
    id: int
    title: str
    camera: str
    description: str
    mood: str
    duration_seconds: int = Field(ge=1, le=20)
    video_prompt: str


class Storyboard(BaseModel):
    title: str
    logline: str
    style: str
    aspect_ratio: AspectRatio
    scenes: List[Scene]
    total_seconds: int
    source: Literal["ai", "mock"]


class RegenerateRequest(BaseModel):
    request: StoryboardRequest
    scene: Scene
    instruction: Optional[str] = None
