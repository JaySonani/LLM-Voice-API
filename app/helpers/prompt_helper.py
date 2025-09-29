from app.models.brand import Brand
from app.models.voice import VoiceProfile


def get_voice_profile_prompt(brand: Brand, site_text: str, samples: list[str]) -> str:

    prompt = f"""
        You are a voice profile generator. You are given a brand name and content from the brand's website and writing samples. You need to generate a comprehensive voice profile for the brand.
        
        Brand Information:
        - Brand Name: {brand.name}
        - Website Content: {site_text}
        - Writing Samples: {" ".join(samples or [])}
        
        Please analyze the provided content to generate a voice profile that captures how the brand "sounds" and communicates. Consider the following aspects:
        
        1. **Voice Metrics** (score each 0.0-1.0, provide up to 2 decimal places):
           - **Warmth**: How friendly, approachable, and emotionally connected the brand feels
           - **Seriousness**: How formal, professional, and business-focused the tone is
           - **Technicality**: How much technical jargon, complexity, or specialized language is used
           - **Formality**: How formal vs. casual the language and structure are
           - **Playfulness**: How much humor, creativity, or light-heartedness is present
        2. **Target Demographic**: Analyze the content to identify who the brand is speaking to (age, interests, needs, etc.)
        3. **Style Guide**: Extract specific writing guidelines and patterns from the content  
        4. **Writing Example**: Create a representative example that embodies the brand's voice
        
        Analyze the language patterns, tone, vocabulary choices, sentence structure, and overall communication style. Look for consistency across different pieces of content.
        
        Output should be a valid JSON object with the following structure:
        {{
            "metrics": {{
                "warmth": 0.00-1.00,
                "seriousness": 0.00-1.00,
                "technicality": 0.00-1.00,
                "formality": 0.00-1.00,
                "playfulness": 0.00-1.00
            }},
            "target_demographic": "Detailed description of the target audience",
            "style_guide": ["guideline1", "guideline2", "guideline3"],
            "writing_example": "A representative example of the brand's writing style"
        }}
        """

    return prompt


def get_voice_evaluation_prompt(voice: VoiceProfile, text: str) -> str:
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

    return prompt
