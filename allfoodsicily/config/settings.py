"""Configuration settings for AllFoodSicily workflow."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Firecrawl non più utilizzato - tutto con Gemini
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Google Docs - REMOVED: Articles are now sent as PDF via Telegram
    # GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    # GOOGLE_DOCS_FOLDER_ID: str = os.getenv("GOOGLE_DOCS_FOLDER_ID", "")
    # GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    # GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    # GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    # GOOGLE_TOKEN_FILE: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    
    # Execution settings
    DAILY_EXECUTION_HOUR: int = int(os.getenv("DAILY_EXECUTION_HOUR", "9"))
    MAX_ARTICLES_PER_RUN: int = int(os.getenv("MAX_ARTICLES_PER_RUN", "5"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Rome")
    
    # Scraping settings
    MAX_CONCURRENT_SCRAPES: int = int(os.getenv("MAX_CONCURRENT_SCRAPES", "5"))  # Limite concorrenza scraping
    
    # Gemini models
    # Modello per generazione testi (analisi topic, articoli)
    # Opzioni: "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"
    # NOTA: gemini-3-flash-preview supporta Google Search grounding (ricerca web integrata)
    GEMINI_TEXT_MODEL: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-3-flash-preview")
    
    # Modello per generazione immagini (Nano Banana Pro)
    # Opzioni: "gemini-3-pro-image-preview", "gemini-2.5-flash-image"
    GEMINI_IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    
    # Image generation settings
    IMAGE_ASPECT_RATIO: str = "16:9"
    IMAGE_SIZE: str = "2K"
    
    # Article settings
    ARTICLE_MIN_WORDS: int = 500
    ARTICLE_MAX_WORDS: int = 800
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate that all required settings are present.

        Returns:
            List of missing required settings (empty if all present)
        """
        missing = []

        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")

        # Google Docs no longer required - articles sent as PDF via Telegram

        return missing


# Global settings instance
settings = Settings()

