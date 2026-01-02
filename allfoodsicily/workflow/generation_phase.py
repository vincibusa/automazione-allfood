"""Phase 4: Generate articles."""

import logging
from typing import List

from services.gemini_client import GeminiClient
from models.schemas import Article, Topic
from config.settings import settings
from utils.logger import logger

logger = logging.getLogger(__name__)


def execute_generation_phase(topics: List[Topic]) -> List[Article]:
    """Execute generation phase for articles (parallelized).
    
    Args:
        topics: List of topics to generate articles for
        
    Returns:
        List of generated articles
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    logger.info(f"✍️  Preparazione generazione articoli...")
    logger.info(f"   📝 Topic da processare: {len(topics)}")
    
    gemini_client = GeminiClient()
    
    articles = []
    max_articles = min(len(topics), settings.MAX_ARTICLES_PER_RUN)
    logger.info(f"   🎯 Genererò fino a {max_articles} articoli")
    logger.info(f"   ⚡ Generazione parallela (max 3 simultanei)")
    logger.info("")
    
    def generate_single_article(topic: Topic, index: int) -> Article:
        """Generate a single article (synchronous)."""
        try:
            logger.info(f"📝 Articolo {index}/{max_articles}: {topic.titolo}")
            logger.info(f"   🎯 Angolo: {topic.angolo}")
            logger.info("   ✍️  Generazione testo articolo...")
            
            article_content = gemini_client.generate_article(topic)
            word_count = len(article_content.split())
            logger.info(f"   ✅ Testo generato: {word_count} parole")
            
            # Create article object without image
            article = Article(
                title=topic.titolo,
                content=article_content,
                topic=topic,
                image_base64=None,  # Immagini rimosse per velocità
                word_count=word_count,
                sources=[]  # Will be populated from topic.fonti
            )
            
            logger.info(f"   ✅ Articolo {index} completato: {topic.titolo}")
            return article
            
        except Exception as e:
            logger.error(f"   ❌ Errore generazione articolo '{topic.titolo}': {str(e)}")
            raise
    
    async def generate_article_async(topic: Topic, index: int) -> Article:
        """Async wrapper for article generation."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, generate_single_article, topic, index),
                    timeout=60.0
                )
                return result
            except asyncio.TimeoutError:
                logger.error(f"   ⏱️  Timeout generazione articolo '{topic.titolo}' dopo 60s")
                raise
            except Exception as e:
                logger.error(f"   ❌ Errore: {str(e)}")
                raise
    
    async def generate_all_articles_parallel():
        """Generate all articles in parallel with concurrency control."""
        semaphore = asyncio.Semaphore(3)  # Max 3 simultanei
        
        async def generate_with_semaphore(topic: Topic, index: int) -> Article:
            async with semaphore:
                logger.info(f"   🔓 Slot disponibile - generazione articolo {index}")
                result = await generate_article_async(topic, index)
                logger.info(f"   🔒 Slot rilasciato - articolo {index} completato")
                logger.info("")
                return result
        
        # Create tasks
        tasks = [
            generate_with_semaphore(topic, i+1)
            for i, topic in enumerate(topics[:max_articles])
        ]
        
        # Execute in parallel
        logger.info(f"⚡ Avvio generazione parallela di {len(tasks)} articoli...")
        import time
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️  Generazione completata in {elapsed:.2f} secondi")
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"   ❌ Articolo {i+1} fallito: {type(result).__name__}")
                continue
            if result:
                articles.append(result)
        
        return articles
    
    # Run async generation
    articles = asyncio.run(generate_all_articles_parallel())
    
    logger.info(f"✅ Generazione completata: {len(articles)}/{max_articles} articoli generati con successo")
    return articles

