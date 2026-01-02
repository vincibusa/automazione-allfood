"""Phase 3: Analyze content and select topics."""

import logging
from typing import List, Dict, Any

from services.gemini_client import GeminiClient
from models.schemas import Topic
from utils.logger import logger

logger = logging.getLogger(__name__)


def execute_analysis_phase(
    search_results: List[Dict[str, Any]],
    scraped_content: List[Dict[str, Any]]
) -> List[Topic]:
    """Execute analysis phase to select topics.
    
    Args:
        search_results: Results from search phase
        scraped_content: Content from scrape phase
        
    Returns:
        List of selected topics
    """
    logger.info(f"🤖 Preparazione analisi con Gemini...")
    logger.info(f"   📊 Input: {len(search_results)} risultati ricerca + {len(scraped_content)} contenuti scrapati")
    
    gemini_client = GeminiClient()
    logger.info("🧠 Analisi contenuti e selezione topic in corso...")
    logger.info("   (Questo può richiedere 30-60 secondi)")
    topics = gemini_client.analyze_topics(search_results, scraped_content)
    
    if topics:
        logger.info(f"✅ Analisi completata: {len(topics)} topic selezionati")
        for i, topic in enumerate(topics, 1):
            logger.info(f"   {i}. {topic.titolo} ({topic.angolo})")
    else:
        logger.warning("⚠️  Nessun topic selezionato dall'analisi")
    
    return topics

