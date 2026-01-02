# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AllFoodSicily is an automated Python workflow for the AllFoodSicily food magazine that:
- Searches for food news in Sicily using Google Gemini with web grounding
- Scrapes monitored Sicilian food/news sites
- Analyzes content and selects 3-5 interesting topics via AI
- Generates article drafts (500-800 words) and images using Gemini
- Saves articles to Google Docs and sends Telegram notifications

## Commands

```bash
# Setup
cd allfoodsicily
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run workflow immediately
python main.py --now

# Run in scheduler mode (daily at 9:00)
python main.py

# Validate configuration
python main.py --validate

# Test Telegram bot
python -c "from services.telegram_bot import TelegramNotifier; TelegramNotifier().send_notification('Test!')"
```

## Architecture

### Workflow Pipeline (5 phases)
1. **Search Phase** (`workflow/search_phase.py`): Uses `GeminiSearch` with Google Search grounding to find food news
2. **Scrape Phase** (`workflow/scrape_phase.py`): Scrapes 8 monitored Sicilian sites in parallel
3. **Analysis Phase** (`workflow/analysis_phase.py`): `GeminiClient` analyzes content and selects 3-5 topics
4. **Generation Phase** (`workflow/generation_phase.py`): Generates articles with `GeminiClient` and images with `ImageGenerator`
5. **Output Phase** (`workflow/output_phase.py`): Saves to Google Docs and sends Telegram summary

### Key Services
- `services/gemini_client.py`: Text generation and topic analysis (prompts for article generation live here)
- `services/gemini_search.py`: Web search using Gemini with Google Search grounding
- `services/image_generator.py`: Image generation using Gemini 3 Pro Image (Nano Banana Pro)
- `services/google_docs.py`: Google Docs API integration
- `services/telegram_bot.py`: Telegram Bot notifications

### Configuration
- `config/settings.py`: All environment variables and settings (Gemini models, image settings, execution params)
- `config/sources.py`: List of monitored Sicilian food sites (4 generalist + 4 specialized)
- `.env`: API keys (GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GOOGLE_DOCS_FOLDER_ID)

### Data Models
- `models/schemas.py`: Pydantic schemas for Topic, Article, WorkflowResult, GoogleDocInfo

## Key Technical Details

- Uses `google-genai` SDK (not the older `google-generativeai`)
- Default text model: `gemini-3-flash-preview` (supports Google Search grounding)
- Default image model: `gemini-3-pro-image-preview` (2K resolution, 16:9 aspect ratio)
- Google Docs auth: Service account preferred (`service_account.json`), OAuth2 as fallback
- Retry logic via `tenacity` in `utils/retry.py` with exponential backoff
- Structured logging with `structlog`, scheduled execution with `schedule`
