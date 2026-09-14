from pydantic import Field
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    tavily_api_key: str = Field(default="", validation_alias="TAVILY_API_KEY")
    groq_model_primary: str = Field(default="", validation_alias="GROQ_MODEL_PRIMARY")
    groq_model_fast: str = Field(default="", validation_alias="GROQ_MODEL_FAST")
    gemini_model_primary: str = Field(default="", validation_alias="GEMINI_MODEL_PRIMARY")
    gemini_model_fallback: str = Field(default="", validation_alias="GEMINI_MODEL_FALLBACK")
    gemini_model_lite: str = Field(default="", validation_alias="GEMINI_MODEL_LITE")

    model_config=SettingsConfigDict(
        env_file=BASE_DIR/ ".env",
        env_file_encoding="utf-8",
    )

settings=Settings()
