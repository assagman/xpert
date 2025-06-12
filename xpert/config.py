from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai.settings import ModelSettings


class DefaultConfig:
    provider = "openrouter"
    model_name = "google/gemini-2.5-flash-preview-05-20"
    model_settings = ModelSettings(temperature=0.7)


DEFAULT_CONFIG_DIR = Path("~/.xpert").expanduser().resolve()
DEFAULT_ENV_FILE = DEFAULT_CONFIG_DIR / ".env"


def load_env_vars(dotenv_path: Optional[str] = str(DEFAULT_ENV_FILE)) -> None:
    """Loads environment variables from a .env file."""
    loaded = load_dotenv(dotenv_path=dotenv_path, override=True)
    if loaded:
        print(f".env file loaded successfully from {dotenv_path}.")
    else:
        print(
            f"No .env file found or it was empty. Please create file: `{DEFAULT_ENV_FILE}`"
        )
