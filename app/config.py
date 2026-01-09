"""配置管理 - 用 pydantic-settings 讀取環境變數"""
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """應用程式設定

    從 .env 檔案讀取環境變數
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    database_url: str = Field(
        ...,
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )
    debug: bool = False
    log_level: str = "info"
    secret_key: str = Field(
        ...,
        min_length=32,
        validation_alias=AliasChoices("SECRET_KEY", "secret_key"),
        description="JWT 簽名金鑰，必須透過環境變數提供",
    )
    cors_origins: list[str] = ["http://localhost:3000"]  # CORS 允許的來源


settings = Settings()
