"""Phase 5: Generate PDFs (no longer saves to Google Docs)."""

import logging
from typing import List

from services.pdf_generator import PDFGenerator
from models.schemas import Article
from utils.logger import logger

logger = logging.getLogger(__name__)


def execute_output_phase(articles: List[Article]) -> List[bytes]:
    """Execute output phase: generate PDFs for articles.

    Note: Google Docs integration has been removed. Articles are now
    delivered as PDF files via Telegram.

    Args:
        articles: List of articles to convert to PDF

    Returns:
        List of PDF bytes (one for each article)
    """
    logger.info(f"📄 Preparing PDF generation...")
    logger.info(f"   📝 Articles to convert: {len(articles)}")

    pdf_generator = PDFGenerator()
    pdf_results = []

    # Generate PDF for each article
    for i, article in enumerate(articles, 1):
        try:
            logger.info(f"📄 Generating PDF {i}/{len(articles)}: {article.title}")

            pdf_bytes = pdf_generator.generate_article_pdf(
                article=article,
                include_image=(article.image_base64 is not None),
                include_sources=True
            )

            pdf_results.append(pdf_bytes)
            logger.info(f"   ✅ PDF generated: {len(pdf_bytes) / 1024:.1f} KB")
            logger.info("")

        except Exception as e:
            logger.error(f"   ❌ Error generating PDF for '{article.title}': {str(e)}")
            logger.info("")
            continue

    logger.info(f"✅ Phase 5 completed: {len(pdf_results)} PDFs generated")
    logger.info(f"   Total size: {sum(len(p) for p in pdf_results) / 1024:.1f} KB")

    return pdf_results
