"""配置管理 - 用 pydantic-settings 讀取環境變數"""
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

    database_url: str
    debug: bool = False
    log_level: str = "info"


settings = Settings()
