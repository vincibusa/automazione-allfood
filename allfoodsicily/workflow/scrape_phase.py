"""Phase 2: Scrape monitored sites using Gemini."""

import logging
from typing import List, Dict, Any

from services.gemini_search import GeminiSearch
from utils.logger import logger

logger = logging.getLogger(__name__)


def execute_scrape_phase() -> List[Dict[str, Any]]:
    """Execute scraping phase for monitored sites using Gemini.
    
    Returns:
        List of scraped content
    """
    logger.info("🕷️  Inizializzazione scraping con Gemini URL Context...")
    
    searcher = GeminiSearch()
    logger.info("⏳ Avvio scraping parallelo dei siti monitorati...")
    content = searcher.scrape_sites_sync()
    
    if content:
        logger.info(f"📊 Scraping completato: {len(content)} siti processati con successo")
        # Mostra riepilogo per tipo
        generalist = sum(1 for c in content if c.get('site_type') == 'generalist')
        specialized = sum(1 for c in content if c.get('site_type') == 'specialized')
        logger.info(f"   📰 Giornali generalisti: {generalist}")
        logger.info(f"   🍝 Siti specializzati: {specialized}")
    else:
        logger.warning("⚠️  Nessun contenuto estratto dai siti")
    
    return content

