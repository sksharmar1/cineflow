"""Video provider layer. Phase 2 plugs real services in here; the MVP ships only a stub."""
from abc import ABC, abstractmethod
from typing import Optional


class VideoProvider(ABC):
    name: str

    @abstractmethod
    async def generate_video(self, prompt: str, image_url: Optional[str] = None, seconds: int = 5) -> str:
        """Return a URL to the generated clip."""


class StubProvider(VideoProvider):
    name = "stub"

    async def generate_video(self, prompt: str, image_url: Optional[str] = None, seconds: int = 5) -> str:
        raise NotImplementedError("No video provider configured yet (Phase 2).")


PROVIDERS = {"stub": StubProvider()}
