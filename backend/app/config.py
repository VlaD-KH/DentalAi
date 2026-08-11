"""
Конфигурация бэкенда и MCP-сервера DentalAi на базе Pydantic Settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Глобальные настройки приложения."""
    PROJECT_NAME: str = "DentalAi Backend & FastMCP Server"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Пути к директориям
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    ORDERS_DIR: Path = DATA_DIR / "orders"
    SCANS_DIR: Path = DATA_DIR / "scans"
    OUTPUT_DIR: Path = DATA_DIR / "output"
    STORAGE_DIR: Path = DATA_DIR / "storage"
    AI_MODELS_DIR: Path = BASE_DIR / "ai-models"

    # База данных и брокер
    DATABASE_URL: str = "postgresql://dental_user:dental_secret_pass@localhost:5432/dental_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # MCP Сервер
    MCP_SERVER_NAME: str = "dental-cadcam-mcp"
    MCP_TRANSPORT: str = "sse"  # "stdio" или "sse"
    MCP_PORT: int = 8000

    # Окружение и железо
    BLENDER_PATH: str = "/usr/bin/blender"
    USE_GPU: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Автоматическое создание необходимых рабочих директорий
for directory in [settings.DATA_DIR, settings.ORDERS_DIR, settings.SCANS_DIR, settings.OUTPUT_DIR, settings.STORAGE_DIR, settings.AI_MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
