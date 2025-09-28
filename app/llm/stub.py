

from datetime import datetime
import hashlib
from uuid import uuid4

from app.llm.ports import LLMPort
from app.models.brand import Brand
from app.models.voice import VoiceEvaluation, VoiceProfile, VoiceSource


class StubLLM(LLMPort):
    """Stub LLM implementation."""

    def _deterministic_score(self, seed: str) -> float:
        """Generate a float between 0-1 based on hash of seed."""
        h = hashlib.sha256(seed.encode()).hexdigest()
        return round(int(h[:8], 16) / 0xFFFFFFFF, 2)

    def generate_voice_profile(
        self, *, brand: Brand, site_text: str | None, samples: list[str] | None
    ) -> VoiceProfile:
        seed_text = (site_text or "") + " ".join(samples or [])

        # Determine voice source based on input presence
        if site_text and samples:
            voice_source = VoiceSource.MIXED
        elif site_text:
            voice_source = VoiceSource.SITE
        else:
            voice_source = VoiceSource.MANUAL

        metrics = {
            "warmth": self._deterministic_score(seed_text + "warmth"),
            "seriousness": self._deterministic_score(seed_text + "seriousness"),
            "technicality": self._deterministic_score(seed_text + "technicality"),
            "formality": self._deterministic_score(seed_text + "formality"),
            "playfulness": self._deterministic_score(seed_text + "playfulness"),
        }

        return VoiceProfile(
            id=str(uuid4()),
            brand_id=brand.id,
            version=1,
            metrics=metrics,
            target_demographic=f"Deterministic demographic for {brand.name}",
            style_guide=[
                f"Always mention {brand.name}", "Keep sentences short"],
            writing_example=f"This is a sample writing style for {brand.name}.",
            llm_model="stub-llm",
            source=voice_source,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def evaluate_text(
        self, *, voice: VoiceProfile, text: str
    ) -> VoiceEvaluation:
        # Compare against expected metrics (simplified)

        scores = {}
        for metric_name in voice.metrics.keys():
            score = self._deterministic_score(text + metric_name)
            scores[metric_name] = score

        suggestions = [
            f"Consider adjusting {k} tone." for k in voice.metrics.keys()]
        return VoiceEvaluation(
            id=str(uuid4()),
            brand_id=voice.brand_id,
            voice_profile_id=voice.id,
            input_text=text,
            scores=scores,
            suggestions=suggestions
        )
