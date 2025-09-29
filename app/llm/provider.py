import json
from uuid import uuid4
from cohere import ChatResponse, ClientV2
from datetime import datetime
from app.configs.settings import settings
from app.helpers.prompt_helper import (
    get_voice_evaluation_prompt,
    get_voice_profile_prompt,
)
from app.helpers.response_schema_helper import (
    voice_evaluation_response_schema,
    voice_profile_response_schema,
)
from app.llm.ports import LLMPort
from app.models.brand import Brand
from app.models.voice import (
    VoiceEvaluation,
    VoiceEvaluationResponseLLM,
    VoiceProfile,
    VoiceProfileMetrics,
    VoiceProfileResponseLLM,
    VoiceSource,
)


class ProviderLLM(LLMPort):
    """Provider LLM implementation."""

    def __init__(self, model):
        self.cohere_client = ClientV2(settings.COHERE_API_KEY)
        self.model = model

    def generate_voice_profile(
        self, *, brand: Brand, site_text: str | None, samples: list[str] | None
    ) -> VoiceProfile | None:

        print("\n\n---> Generating voice profile with Cohere LLM...")
        prompt = get_voice_profile_prompt(brand, site_text, samples)
        llm_response: ChatResponse = self.cohere_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=voice_profile_response_schema,
        )

        if llm_response.finish_reason == "COMPLETE":
            try:
                # Extract text content from the response
                response_text = (
                    llm_response.message.content[0].text
                    if llm_response.message.content
                    else ""
                )
                if not response_text:
                    raise ValueError("Empty response from LLM")
                json_response = json.loads(response_text)
                voice_profile = VoiceProfileResponseLLM(**json_response)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse LLM response as JSON: {e}")
            except Exception as e:
                raise ValueError(
                    f"Unexpected error during voice profile generation: {e}"
                )
        else:
            raise ValueError(
                f"LLM response incomplete, finish_reason: {llm_response.finish_reason}"
            )

        metrics_dict: VoiceProfileMetrics = {
            "warmth": voice_profile.metrics.warmth,
            "seriousness": voice_profile.metrics.seriousness,
            "technicality": voice_profile.metrics.technicality,
            "formality": voice_profile.metrics.formality,
            "playfulness": voice_profile.metrics.playfulness,
        }
        return VoiceProfile(
            id=str(uuid4()),
            brand_id=brand.id,
            version=1,
            metrics=metrics_dict,
            target_demographic=voice_profile.target_demographic,
            style_guide=voice_profile.style_guide,
            writing_example=voice_profile.writing_example,
            llm_model=self.model,
            source=VoiceSource.MIXED,  # Since we're using both site text and writing samples
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def evaluate_text(
        self, *, voice_profile: VoiceProfile, text: str
    ) -> VoiceEvaluation:
        """Evaluate text against a voice profile using Cohere LLM."""

        print("\n\n---> Evaluating text with CohereLLM...")
        prompt = get_voice_evaluation_prompt(voice_profile, text)
        llm_response: ChatResponse = self.cohere_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=voice_evaluation_response_schema,
        )

        if llm_response.finish_reason == "COMPLETE":
            try:
                response_text = (
                    llm_response.message.content[0].text
                    if llm_response.message.content
                    else ""
                )
                if not response_text:
                    raise ValueError("Empty response from LLM")
                json_response = json.loads(response_text)
                voice_evaluation = VoiceEvaluationResponseLLM(**json_response)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse LLM response as JSON: {e}")
            except Exception as e:
                raise ValueError(f"Unexpected error during text evaluation: {e}")
        else:
            raise ValueError(
                f"LLM response incomplete, finish_reason: {llm_response.finish_reason}"
            )

        scores_dict = {
            "warmth": voice_evaluation.scores.warmth,
            "seriousness": voice_evaluation.scores.seriousness,
            "technicality": voice_evaluation.scores.technicality,
            "formality": voice_evaluation.scores.formality,
            "playfulness": voice_evaluation.scores.playfulness,
        }
        return VoiceEvaluation(
            id=str(uuid4()),
            brand_id=voice_profile.brand_id,
            voice_profile_id=voice_profile.id,
            input_text=text,
            scores=scores_dict,
            suggestions=voice_evaluation.suggestions,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
