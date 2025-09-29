from typing import Protocol

from app.models.brand import Brand
from app.models.voice import VoiceEvaluation, VoiceProfile


class LLMPort(Protocol):
    """Port for LLM operations."""

    def generate_voice_profile(
        self, *, brand: Brand, site_text: str | None, samples: list[str] | None
    ) -> VoiceProfile: ...

    def evaluate_text(self, *, voice: VoiceProfile, text: str) -> VoiceEvaluation: ...
