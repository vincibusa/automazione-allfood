"""Manual workflow for topic-based article generation via Telegram."""

import logging
import asyncio
from typing import Tuple, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from services.gemini_client import GeminiClient
from services.gemini_search import GeminiSearch
from services.image_generator import ImageGenerator
from services.pdf_generator import PDFGenerator
from models.schemas import Article, Topic, TopicSource

logger = logging.getLogger(__name__)


async def execute_manual_workflow(topic_text: str) -> Tuple[Article, bytes]:
    """Execute workflow for a manually specified topic.

    This workflow:
    1. Researches the topic using Gemini Search
    2. Generates an article about the topic
    3. Generates an image for the article
    4. Creates a PDF document

    Args:
        topic_text: Topic description from user (e.g., "arancini siciliani")

    Returns:
        Tuple of (Article object, PDF bytes)

    Raises:
        Exception: If any step fails
    """
    logger.info("=" * 60)
    logger.info(f"Starting manual workflow for topic: '{topic_text}'")
    logger.info("=" * 60)

    # Initialize services
    gemini_client = GeminiClient()
    gemini_search = GeminiSearch()
    image_generator = ImageGenerator()
    pdf_generator = PDFGenerator()

    # Step 1: Research topic with Gemini Search
    logger.info("")
    logger.info("📚 STEP 1: Researching topic with Gemini Search")
    logger.info("-" * 60)
    search_results = await _research_topic(gemini_search, topic_text)
    logger.info(f"✅ Found {len(search_results)} sources")

    # Step 2: Create topic object
    logger.info("")
    logger.info("📋 STEP 2: Creating topic structure")
    logger.info("-" * 60)
    topic = _create_topic_from_results(topic_text, search_results)
    logger.info(f"✅ Topic created: {topic.titolo}")
    logger.info(f"   Keywords: {', '.join(topic.keywords)}")
    logger.info(f"   Sources: {len(topic.fonti)}")

    # Step 3: Generate article
    logger.info("")
    logger.info("✍️  STEP 3: Generating article with Gemini")
    logger.info("-" * 60)
    article_content = await _generate_article_async(gemini_client, topic)
    word_count = len(article_content.split())
    logger.info(f"✅ Article generated: {word_count} words")

    # Step 4: Generate image
    logger.info("")
    logger.info("🎨 STEP 4: Generating image with Gemini Image")
    logger.info("-" * 60)
    image_base64 = None
    try:
        image_prompt = gemini_client.generate_image_prompt(topic, article_content)
        logger.info(f"   Image prompt: {image_prompt[:80]}...")

        image_base64, mime_type = await _generate_image_async(image_generator, image_prompt)
        logger.info(f"✅ Image generated: {len(image_base64)} chars base64")
    except Exception as e:
        logger.warning(f"⚠️  Image generation failed: {e}")
        logger.info("   Continuing without image...")

    # Step 5: Create article object
    logger.info("")
    logger.info("📦 STEP 5: Creating article object")
    logger.info("-" * 60)

    # Convert search results to TopicSource
    sources = []
    for result in search_results[:5]:  # Top 5 sources
        try:
            source = TopicSource(
                url=result.get('url', ''),
                title=result.get('title'),
                snippet=result.get('snippet')
            )
            sources.append(source)
        except Exception as e:
            logger.warning(f"   Could not create source: {e}")

    article = Article(
        title=topic.titolo,
        content=article_content,
        topic=topic,
        image_base64=image_base64,
        word_count=word_count,
        sources=sources
    )
    logger.info(f"✅ Article object created")

    # Step 6: Generate PDF
    logger.info("")
    logger.info("📄 STEP 6: Generating PDF document")
    logger.info("-" * 60)
    pdf_bytes = pdf_generator.generate_article_pdf(
        article,
        include_image=(image_base64 is not None),
        include_sources=True
    )
    logger.info(f"✅ PDF generated: {len(pdf_bytes)} bytes ({len(pdf_bytes) / 1024:.1f} KB)")

    logger.info("")
    logger.info("=" * 60)
    logger.info("🎉 Manual workflow completed successfully!")
    logger.info(f"   Title: {article.title}")
    logger.info(f"   Words: {article.word_count}")
    logger.info(f"   Image: {'Yes' if image_base64 else 'No'}")
    logger.info(f"   PDF size: {len(pdf_bytes) / 1024:.1f} KB")
    logger.info("=" * 60)

    return article, pdf_bytes


async def _research_topic(searcher: GeminiSearch, topic: str) -> List[Dict[str, Any]]:
    """Research a topic using Gemini Search.

    Args:
        searcher: GeminiSearch instance
        topic: Topic to research

    Returns:
        List of search results
    """
    loop = asyncio.get_event_loop()

    # Construct search query with Sicilian food context
    query = f"{topic} Sicilia food gastronomia cucina"

    # Run synchronous search in executor
    def search():
        return searcher._search_single_query(
            query=query,
            days_back=30,  # Look back 30 days
            limit=10,
            query_index=1,
            total_queries=1
        )

    with ThreadPoolExecutor() as executor:
        results = await loop.run_in_executor(executor, search)

    return results if results else []


def _create_topic_from_results(
    topic_text: str,
    search_results: List[Dict[str, Any]]
) -> Topic:
    """Create a Topic object from search results.

    Args:
        topic_text: User-provided topic text
        search_results: Search results from Gemini Search

    Returns:
        Topic object
    """
    # Extract URLs from search results
    fonti = []
    for result in search_results[:5]:  # Top 5 sources
        url = result.get('url', '')
        if url:
            fonti.append(url)

    # Extract keywords from topic
    keywords = _extract_keywords(topic_text)

    # Create topic
    topic = Topic(
        titolo=topic_text.title(),
        angolo="articolo su richiesta",
        fonti=fonti,
        keywords=keywords
    )

    return topic


def _extract_keywords(topic: str) -> List[str]:
    """Extract keywords from topic text.

    Args:
        topic: Topic text

    Returns:
        List of keywords
    """
    # Simple keyword extraction
    words = topic.lower().split()

    # Italian stopwords
    stopwords = {
        'un', 'una', 'il', 'la', 'i', 'le', 'gli', 'lo',
        'di', 'da', 'in', 'su', 'per', 'con', 'tra', 'fra',
        'e', 'o', 'ma', 'se', 'che', 'del', 'della', 'dei',
        'delle', 'al', 'alla', 'ai', 'alle', 'sul', 'sulla',
        'sui', 'sulle', 'nel', 'nella', 'nei', 'nelle'
    }

    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    # Add "Sicilia" if not already present
    if 'sicilia' not in [k.lower() for k in keywords]:
        keywords.append('Sicilia')

    return keywords[:5]  # Max 5 keywords


async def _generate_article_async(
    client: GeminiClient,
    topic: Topic
) -> str:
    """Generate article asynchronously.

    Args:
        client: GeminiClient instance
        topic: Topic to write about

    Returns:
        Article content as markdown string
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor() as executor:
        article_content = await loop.run_in_executor(
            executor,
            client.generate_article,
            topic
        )

    return article_content


async def _generate_image_async(
    generator: ImageGenerator,
    prompt: str
) -> Tuple[str, str]:
    """Generate image asynchronously.

    Args:
        generator: ImageGenerator instance
        prompt: Image generation prompt

    Returns:
        Tuple of (base64_string, mime_type)
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            generator.generate_image_base64,
            prompt
        )

    return result
