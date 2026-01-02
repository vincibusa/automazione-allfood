"""Phase 1: Search for food news using Gemini."""

import logging
from typing import List, Dict, Any

from services.gemini_search import GeminiSearch
from utils.logger import logger

logger = logging.getLogger(__name__)


def execute_search_phase(days_back: int = 7) -> List[Dict[str, Any]]:
    """Execute search phase for food news using Gemini with Google Search.
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        List of search results
    """
    logger.info(f"🔍 Inizializzazione ricerca con Gemini (ultimi {days_back} giorni)...")
    
    searcher = GeminiSearch()
    logger.info("🔎 Esecuzione ricerche web...")
    results = searcher.search_food_news(days_back=days_back)
    
    if results:
        logger.info(f"📊 Trovati {len(results)} risultati unici")
        # Mostra primi 3 risultati come esempio
        for i, result in enumerate(results[:3], 1):
            logger.info(f"   {i}. {result.get('title', 'N/A')[:60]}...")
        if len(results) > 3:
            logger.info(f"   ... e altri {len(results) - 3} risultati")
    else:
        logger.warning("⚠️  Nessun risultato trovato")
    
    return results

