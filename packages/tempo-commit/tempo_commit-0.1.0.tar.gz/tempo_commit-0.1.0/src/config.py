from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    jira_url: str = "https://jira.atlassian.com"
    jira_email: str
    jira_api_token: str
    tempo_api_token: str
    timezone: str = "Asia/Almaty"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


@lru_cache
def get_settings():
    return Settings()
