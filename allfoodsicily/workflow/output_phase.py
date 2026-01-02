"""Phase 5: Save to Google Docs and send notifications."""

import logging
from typing import List
from datetime import datetime

from services.google_docs import GoogleDocsService
from services.telegram_bot import TelegramNotifier
from models.schemas import Article, GoogleDocInfo
from config.sources import ALL_SITES
from utils.logger import logger

logger = logging.getLogger(__name__)


def execute_output_phase(articles: List[Article]) -> List[GoogleDocInfo]:
    """Execute output phase: save to Google Docs and notify.
    
    Args:
        articles: List of articles to save
        
    Returns:
        List of created Google Docs
    """
    logger.info(f"📄 Preparazione salvataggio su Google Docs...")
    logger.info(f"   📝 Articoli da salvare: {len(articles)}")
    
    docs_service = GoogleDocsService()
    telegram_notifier = TelegramNotifier()
    
    docs = []
    
    # Save each article to Google Docs
    for i, article in enumerate(articles, 1):
        try:
            logger.info(f"💾 Salvataggio articolo {i}/{len(articles)}: {article.title}")
            logger.info("   📄 Creazione documento Google Docs...")
            
            doc_info = docs_service.create_document(
                article=article,
                image_base64=article.image_base64,
                image_mime_type="image/png"  # Default, could be improved
            )
            
            docs.append(doc_info)
            logger.info(f"   ✅ Documento creato: {doc_info.doc_url}")
            logger.info("")
            
        except Exception as e:
            logger.error(f"   ❌ Errore salvataggio articolo '{article.title}': {str(e)}")
            logger.info("")
            continue
    
    logger.info(f"📱 Invio notifica Telegram...")
    logger.info(f"✅ Fase 5 completata: {len(docs)} documenti creati")
    return docs

