from pydantic_ai.settings import ModelSettings


class DefaultConfig:
    provider = "openrouter"
    model_name = "google/gemini-2.5-flash-preview-05-20"
    model_settings = ModelSettings(
        temperature=0.7
    )
