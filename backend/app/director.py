"""AI Director: turns an idea into a shot-by-shot storyboard.

Uses Claude when ANTHROPIC_API_KEY is set; otherwise returns a deterministic
mock storyboard so the UI and deployment can be verified without spending credits.
"""
import json
import os
import re
from typing import Optional

from .models import RegenerateRequest, Scene, Storyboard, StoryboardRequest

MODEL = os.getenv("CINEFLOW_MODEL", "claude-sonnet-5-5")

SYSTEM = """You are an award-winning film director and screenwriter. Turn the user's idea into a
shot-by-shot storyboard for a short AI-generated film. Respond with ONLY valid JSON, no prose,
matching this schema:
{"title": str, "logline": str, "scenes": [{"title": str, "camera": str, "description": str,
"mood": str, "duration_seconds": int, "video_prompt": str}]}
Rules: scene durations must sum to the requested length (+/- 2s); use 3-8 scenes; vary camera
angles (wide establishing, close-up, tracking, over-the-shoulder, etc.); video_prompt must be a
self-contained text-to-video prompt including subject, action, camera, lighting and the visual style."""


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Model did not return JSON")
    return json.loads(match.group(0))


def _build(req: StoryboardRequest, data: dict, source: str) -> Storyboard:
    scenes = [
        Scene(
            id=i + 1,
            title=s["title"],
            camera=s["camera"],
            description=s["description"],
            mood=s["mood"],
            duration_seconds=max(1, min(20, int(s["duration_seconds"]))),
            video_prompt=s["video_prompt"],
        )
        for i, s in enumerate(data["scenes"])
    ]
    return Storyboard(
        title=data["title"],
        logline=data["logline"],
        style=req.style,
        aspect_ratio=req.aspect_ratio,
        scenes=scenes,
        total_seconds=sum(s.duration_seconds for s in scenes),
        source=source,  # type: ignore[arg-type]
    )


def _mock(req: StoryboardRequest) -> Storyboard:
    n = max(3, min(6, req.length_seconds // 8))
    per = max(2, req.length_seconds // n)
    beats = [
        ("Establishing", "Wide establishing shot", "Set the world and tone"),
        ("Inciting moment", "Close-up", "Something unexpected happens"),
        ("Rising tension", "Tracking shot", "The stakes grow"),
        ("Turning point", "Over-the-shoulder", "A decision is made"),
        ("Climax", "Low-angle hero shot", "Peak intensity"),
        ("Resolution", "Slow pull-back", "Aftermath and reflection"),
    ][:n]
    scenes = [
        {
            "title": t,
            "camera": cam,
            "description": f"{mood}: {req.idea[:120]}",
            "mood": req.genre,
            "duration_seconds": per,
            "video_prompt": f"{cam}, {req.genre} film, {req.style} look. {req.idea[:160]}. {mood}.",
        }
        for t, cam, mood in beats
    ]
    return _build(req, {"title": req.idea[:48].rstrip(".") , "logline": req.idea, "scenes": scenes}, "mock")


def _client():
    import anthropic

    return anthropic.Anthropic()


def generate_storyboard(req: StoryboardRequest) -> Storyboard:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return _mock(req)
    prompt = (
        f"Idea: {req.idea}\nGenre: {req.genre}\nTotal length: {req.length_seconds} seconds\n"
        f"Visual style: {req.style}\nAspect ratio: {req.aspect_ratio}"
    )
    msg = _client().messages.create(
        model=MODEL, max_tokens=3000, system=SYSTEM, messages=[{"role": "user", "content": prompt}]
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return _build(req, _extract_json(text), "ai")


def regenerate_scene(body: RegenerateRequest) -> Scene:
    req, old = body.request, body.scene
    if not os.getenv("ANTHROPIC_API_KEY"):
        return old.model_copy(
            update={"description": f"(alt take) {old.description}", "video_prompt": f"Alternate angle. {old.video_prompt}"}
        )
    prompt = (
        f"Film idea: {req.idea}\nGenre: {req.genre}\nStyle: {req.style}\n"
        f"Rewrite ONLY this scene with a fresh take, keeping duration {old.duration_seconds}s.\n"
        f"Current scene: {old.model_dump_json()}\nExtra direction: {body.instruction or 'none'}\n"
        'Return ONLY JSON: {"title","camera","description","mood","duration_seconds","video_prompt"}'
    )
    msg = _client().messages.create(
        model=MODEL, max_tokens=1000, system=SYSTEM, messages=[{"role": "user", "content": prompt}]
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    d: Optional[dict] = _extract_json(text)
    return Scene(id=old.id, **{k: d[k] for k in ("title", "camera", "description", "mood", "duration_seconds", "video_prompt")})
