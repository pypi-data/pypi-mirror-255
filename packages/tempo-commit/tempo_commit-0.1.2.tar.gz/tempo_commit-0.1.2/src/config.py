import os
from dataclasses import dataclass, fields
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


@dataclass
class Settings:
    jira_url: str = "https://jira.atlassian.com"
    jira_email: str = None
    jira_api_token: str = None
    tempo_api_token: str = None

    def __post_init__(self):
        for field in fields(self):
            value = os.getenv(field.name.upper(), None)
            if value is None and field.default is None:
                raise ValueError(f"{field.name} is required.")
            setattr(self, field.name, value)


@lru_cache
def get_settings():
    return Settings()
