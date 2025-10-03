"""Configuration settings using Pydantic."""

from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API configuration."""

    base_url: str = "https://community.shopify.dev"
    rate_limit: float = 1.0
    timeout: float = 30.0
    max_retries: int = 3


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = "sqlite:///data/database/forum.db"
    echo: bool = False


class ScrapingSettings(BaseSettings):
    """Scraping configuration."""

    batch_size: int = 100
    checkpoint_interval: int = 10
    checkpoint_dir: str = "data/checkpoints"


class CategoryConfig(BaseSettings):
    """Category configuration."""

    id: int
    name: str
    slug: str


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/forum_analyzer.log"


class AskSettings(BaseSettings):
    """Settings for the ask command."""

    context_limit: int = 50
    cache_queries: bool = True


class LLMAnalysisSettings(BaseSettings):
    """LLM analysis settings."""

    api_key: str = ""
    model: str = "claude-opus-4"
    batch_size: int = 10
    max_tokens: int = 4096
    temperature: float = 0.0
    theme_context_limit: int = 50
    ask: AskSettings = Field(default_factory=AskSettings)


class Settings(BaseSettings):
    """Main application settings."""

    api: APISettings = Field(default_factory=APISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    categories: List[CategoryConfig] = Field(default_factory=list)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    llm_analysis: LLMAnalysisSettings = Field(default_factory=LLMAnalysisSettings)

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Settings":
        """Load settings from YAML file.

        Args:
            config_path: Path to YAML config file

        Returns:
            Settings instance
        """
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls(
            api=APISettings(**config_data.get("api", {})),
            database=DatabaseSettings(**config_data.get("database", {})),
            scraping=ScrapingSettings(**config_data.get("scraping", {})),
            categories=[
                CategoryConfig(**cat) for cat in config_data.get("categories", [])
            ],
            logging=LoggingSettings(**config_data.get("logging", {})),
            llm_analysis=LLMAnalysisSettings(**config_data.get("llm_analysis", {})),
        )


_settings: Optional[Settings] = None


def get_settings(config_path: Optional[Path] = None) -> Settings:
    """Get application settings (singleton pattern).

    Args:
        config_path: Optional path to config file

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None:
        if config_path is None:
            config_path = Path("config/config.yaml")

        if config_path.exists():
            _settings = Settings.from_yaml(config_path)
        else:
            _settings = Settings()

    return _settings
