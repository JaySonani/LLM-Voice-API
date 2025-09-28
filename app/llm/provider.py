from datetime import datetime
import json
import os
from app.configs.settings import settings
from app.llm.ports import LLMPort
from app.models.brand import Brand
from app.models.voice import (
    VoiceEvaluation,
    VoiceProfile,
    VoiceProfileMetrics,
    VoiceProfileResponseLLM,
    VoiceSource,
)
from uuid import uuid4

from cohere import ChatResponse, ClientV2


class ProviderLLM(LLMPort):
    """Provider LLM implementation."""

    def __init__(self, model):
        self.cohere_client = ClientV2(settings.COHERE_API_KEY)
        self.model = model

    def generate_voice_profile(
        self, *, brand: Brand, site_text: str | None, samples: list[str] | None
    ) -> VoiceProfile | None:

        prompt = f"""
            You are a voice profile generator. You are given a brand name and a bunch of text scraped from the brand's website. You need to generate a voice profile for the brand.
            The voice profile should be a description of the brand's voice and tone. The voice profile is how the brand "sounds" like.

            Brand name: {brand.name}
            Site text: {site_text}
            Writing samples: {" ".join(samples or [])}

            Analyze the site text and writing samples to generate the voice profile.

            The voice profile should be in the following format:
            {voice_profile_example}
            Above is just an example. You need to generate the voice profile based on the brand name, site text, and writing samples, but follow the format above.
            Output should be a valid JSON object, with double quotes for the keys.


            The metrics should be a score between 0 and 1 for each metric.
            The target_demographic should be a description of the target audience for the brand.
            The style_guide should be a list of style guidelines for the brand.
            The writing_example should be an example of the brand's writing style.

            """

        print("\n\n---> Generating voice profile with Cohere LLM...")

        llm_response: ChatResponse = self.cohere_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_object",
                "json_schema": {
                    "type": "object",
                    "required": [
                        "metrics",
                        "target_demographic",
                        "style_guide",
                        "writing_example",
                    ],
                    "properties": {
                        "metrics": {
                            "type": "object",
                            "required": [
                                "warmth",
                                "seriousness",
                                "technicality",
                                "formality",
                                "playfulness",
                            ],
                            "properties": {
                                "warmth": {"type": "number"},
                                "seriousness": {"type": "number"},
                                "technicality": {"type": "number"},
                                "formality": {"type": "number"},
                                "playfulness": {"type": "number"},
                            },
                        },
                        "target_demographic": {"type": "string"},
                        "style_guide": {"type": "array", "items": {"type": "string"}},
                        "writing_example": {"type": "string"},
                    },
                },
            },
        )

        voice_profile = None
        if llm_response.finish_reason == "COMPLETE":
            try:
                # Extract text content from the response
                response_text = (
                    llm_response.message.content[0].text
                    if llm_response.message.content
                    else ""
                )
                json_response = json.loads(response_text)
                voice_profile = VoiceProfileResponseLLM(**json_response)

            except json.JSONDecodeError as e:
                print(f"\n\nJSON parsing error: {e}")
                print(f"\n\nRaw response that failed to parse: {response_text}")
            except Exception as e:
                print(f"Unexpected error: {e}")

        # Use parsed JSON response or fallback to example
        if voice_profile:
            # Convert VoiceProfileMetrics object to dictionary
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
                updated_at=datetime.now()
            )


    def evaluate_text(self, *, voice: VoiceProfile, text: str) -> VoiceEvaluation:
        """Evaluate text against a voice profile using Cohere LLM."""
        
        prompt = f"""
        You are a voice evaluation expert. You need to evaluate a piece of text against a brand's voice profile.
        
        Voice Profile Details:
        - Target Demographic: {voice.target_demographic}
        - Style Guide: {', '.join(voice.style_guide)}
        - Writing Example: {voice.writing_example}
        - Expected Metrics:
          - Warmth: {voice.metrics['warmth']}
          - Seriousness: {voice.metrics['seriousness']}
          - Technicality: {voice.metrics['technicality']}
          - Formality: {voice.metrics['formality']}
          - Playfulness: {voice.metrics['playfulness']}
        
        Text to Evaluate:
        {text}
        
        Please analyze the text and provide:
        1. Scores for each metric (0-1 scale) based on how well the text matches the expected voice profile
        2. Specific suggestions for improvement
        
        The scores should reflect how closely the text aligns with the brand's voice profile.
        A score of 1.0 means perfect alignment, 0.0 means complete misalignment. Provide score upto 2 decimal places.
        
        Output should be a valid JSON object with the following structure:
        {{
            "scores": {{
                "warmth": 0.00-1.00,
                "seriousness": 0.0-1.0,
                "technicality": 0.00-1.00,
                "formality": 0.00-1.00,
                "playfulness": 0.00-1.00
            }},
            "suggestions": ["suggestion1", "suggestion2", ...]
        }}
        """

        print("\n\n---> Evaluating text with CohereLLM...")

        llm_response: ChatResponse = self.cohere_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_object",
                "json_schema": {
                    "type": "object",
                    "required": ["scores", "suggestions"],
                    "properties": {
                        "scores": {
                            "type": "object",
                            "required": [
                                "warmth",
                                "seriousness", 
                                "technicality",
                                "formality",
                                "playfulness",
                            ],
                            "properties": {
                                "warmth": {"type": "number"},
                                "seriousness": {"type": "number"},
                                "technicality": {"type": "number"},
                                "formality": {"type": "number"},
                                "playfulness": {"type": "number"},
                            },
                        },
                        "suggestions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
        )

        # Default fallback values
        default_scores = {
            "warmth": 0.5,
            "seriousness": 0.5,
            "technicality": 0.5,
            "formality": 0.5,
            "playfulness": 0.5,
        }
        default_suggestions = ["Review the text against the brand's style guide"]

        if llm_response.finish_reason == "COMPLETE":
            try:
                # Extract text content from the response
                response_text = (
                    llm_response.message.content[0].text
                    if llm_response.message.content
                    else ""
                )
                json_response = json.loads(response_text)
                
                # Validate and use the response
                scores = json_response.get("scores", default_scores)
                suggestions = json_response.get("suggestions", default_suggestions)
                
                # Ensure all required metrics are present
                for metric in ["warmth", "seriousness", "technicality", "formality", "playfulness"]:
                    if metric not in scores:
                        scores[metric] = default_scores[metric]
                    # Clamp scores to 0-1 range
                    scores[metric] = max(0.0, min(1.0, float(scores[metric])))

            except json.JSONDecodeError as e:
                print(f"\n\nJSON parsing error in evaluate_text: {e}")
                print(f"\n\nRaw response that failed to parse: {response_text}")
                scores = default_scores
                suggestions = default_suggestions
            except Exception as e:
                print(f"Unexpected error in evaluate_text: {e}")
                scores = default_scores
                suggestions = default_suggestions
        else:
            print(f"LLM response incomplete, finish_reason: {llm_response.finish_reason}")
            scores = default_scores
            suggestions = default_suggestions

        return VoiceEvaluation(
            id=str(uuid4()),
            brand_id=voice.brand_id,
            voice_profile_id=voice.id,
            input_text=text,
            scores=scores,
            suggestions=suggestions,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )


voice_profile_example = {
    "metrics": {
        "warmth": 0.012165765746535212,
        "seriousness": 0.19004976171768498,
        "technicality": 0.23913552198538918,
        "formality": 0.3952317236445918,
        "playfulness": 0.423436887660864,
    },
    "target_demographic": "Young adults between the ages of 18 and 24",
    "style_guide": ["Keep sentences short", "Use conversational tone"],
    "writing_example": "This is a sample writing style for the brand.",
}
