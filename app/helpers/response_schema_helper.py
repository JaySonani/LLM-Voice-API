voice_profile_response_schema = {
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
}

voice_evaluation_response_schema = {
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
}
