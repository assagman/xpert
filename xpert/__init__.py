from typing import Optional
from pathlib import Path

from dotenv import load_dotenv


__version__ = "0.1.1"


DEFAULT_CONFIG_DIR = Path("~/.xpert").expanduser().resolve()
DEFAULT_ENV_FILE = DEFAULT_CONFIG_DIR / ".env"


def load_env_vars(dotenv_path: Optional[str] = str(DEFAULT_ENV_FILE)) -> None:
    """Loads environment variables from a .env file."""
    loaded = load_dotenv(dotenv_path=dotenv_path, override=True)
    if loaded:
        print(f".env file loaded successfully from {dotenv_path}.")
    else:
        print(f"No .env file found or it was empty. Please create file: `{DEFAULT_ENV_FILE}`")
