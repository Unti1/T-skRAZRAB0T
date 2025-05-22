import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ROOT_PATH: Path = Path(__file__).parent.parent
    MEDIA_PATH: Path = ROOT_PATH / 'static' / 'media'
    # host settings
    TUNA_API: str

    # ai settings
    GPT_TOKEN: str
    TOGETHER_API_KEY: str
    DEEPSEEK_API: str

    # proxy settings
    PROXY_LOGIN: str
    PROXY_PASS: str
    PROXY_IP: str
    PROXY_PORT: str

    
    DTFORMAT: str = '%d.%m.%Y %H:%M'

    model_config = SettingsConfigDict(
        env_file=ROOT_PATH / ".env", env_file_encoding="utf-8"
    )

settings = Settings()
