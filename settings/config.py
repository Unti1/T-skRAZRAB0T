import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ROOT_PATH: Path = Path(__file__).parent.parent
    MEDIA_PATH: Path = ROOT_PATH / 'static' / 'media'

    TELEGRAM_API: str
    
    DTFORMAT: str = '%d.%m.%Y %H:%M'

    model_config = SettingsConfigDict(
        env_file=ROOT_PATH / ".env", env_file_encoding="utf-8"
    )

settings = Settings()
