"""PDF generation service for articles."""

import io
import base64
import logging
import re
from typing import Optional
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from models.schemas import Article
from config.settings import settings

logger = logging.getLogger(__name__)


class ArticlePDF(FPDF):
    """Custom PDF class for articles with AllFoodSicily branding."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(left=15, top=15, right=15)

    def header(self):
        """PDF header with AllFoodSicily branding."""
        # Logo text (can be replaced with actual logo image)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(200, 50, 50)  # Rosso
        self.cell(0, 10, 'ALLFOODSICILY', align='C', ln=True)

        # Date
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 100, 100)  # Grigio
        self.cell(0, 5, datetime.now().strftime('%d %B %Y'), align='C', ln=True)

        # Line separator
        self.set_draw_color(200, 200, 200)
        self.line(15, self.get_y() + 2, 195, self.get_y() + 2)
        self.ln(5)

    def footer(self):
        """PDF footer."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Generato da AllFoodSicily AI - https://allfoodsicily.it', align='C')


class PDFGenerator:
    """Service for generating article PDFs."""

    def __init__(self):
        """Initialize PDF generator."""
        logger.info("Initialized PDF generator")

    def generate_article_pdf(
        self,
        article: Article,
        include_image: bool = True,
        include_sources: bool = True
    ) -> bytes:
        """Generate PDF for an article.

        Args:
            article: Article to convert to PDF
            include_image: Whether to include the generated image
            include_sources: Whether to include sources list

        Returns:
            PDF as bytes
        """
        logger.info(f"Generating PDF for article: {article.title}")

        pdf = ArticlePDF()
        pdf.add_page()

        # Add image if available
        if include_image and article.image_base64:
            try:
                self._add_image(pdf, article.image_base64)
            except Exception as e:
                logger.warning(f"Could not add image to PDF: {e}")

        # Add title
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, article.title, align='L')
        pdf.ln(3)

        # Add metadata line
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        metadata = f"{article.word_count} parole"
        if article.topic.keywords:
            metadata += f" | {', '.join(article.topic.keywords[:3])}"
        pdf.cell(0, 5, metadata, ln=True)
        pdf.ln(5)

        # Add content
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(40, 40, 40)

        # Parse and clean markdown content
        content = self._clean_markdown(article.content)

        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                pdf.multi_cell(0, 6, para.strip())
                pdf.ln(4)

        # Add sources section if requested
        if include_sources and article.topic.fonti:
            pdf.ln(5)
            self._add_sources_section(pdf, article.topic.fonti)

        # Output to bytes
        pdf_bytes = pdf.output()
        logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")

        return bytes(pdf_bytes)

    def _add_image(self, pdf: FPDF, image_base64: str) -> None:
        """Add image to PDF from base64.

        Args:
            pdf: FPDF instance
            image_base64: Base64 encoded image
        """
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_base64)

            # Open with PIL to get dimensions
            image = Image.open(io.BytesIO(image_bytes))

            # Calculate dimensions to fit page width
            page_width = pdf.w - 2 * pdf.l_margin
            aspect_ratio = image.height / image.width
            img_width = page_width
            img_height = page_width * aspect_ratio

            # Max height check (don't let image take more than 100mm)
            max_height = 100
            if img_height > max_height:
                img_height = max_height
                img_width = img_height / aspect_ratio

            # Center image
            x_offset = (pdf.w - img_width) / 2

            # Add image directly from BytesIO
            pdf.image(io.BytesIO(image_bytes), x=x_offset, w=img_width, h=img_height)
            pdf.ln(5)

            logger.info(f"Added image to PDF: {img_width:.1f}x{img_height:.1f}mm")

        except Exception as e:
            logger.error(f"Error adding image to PDF: {e}")
            raise

    def _add_sources_section(self, pdf: FPDF, fonti: list) -> None:
        """Add sources section to PDF.

        Args:
            pdf: FPDF instance
            fonti: List of source URLs
        """
        # Section header
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, 'FONTI:', ln=True)

        # Sources list
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 139)  # Dark blue for links

        for fonte in fonti:
            # Truncate very long URLs
            display_url = fonte if len(fonte) < 80 else fonte[:77] + '...'
            pdf.cell(5)  # Indent
            pdf.multi_cell(0, 5, f"- {display_url}")

        logger.info(f"Added {len(fonti)} sources to PDF")

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown formatting for plain text PDF.

        Args:
            text: Markdown text

        Returns:
            Cleaned text suitable for PDF
        """
        # Remove header markers but keep the text
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove bold/italic markers
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)

        # Convert links to text only (keep description, remove URL)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove list markers (will be plain paragraphs)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Clean up multiple newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove any remaining markdown artifacts
        text = re.sub(r'```[a-z]*\n', '', text)
        text = re.sub(r'```', '', text)

        return text.strip()

    def save_pdf_to_file(
        self,
        pdf_bytes: bytes,
        filepath: str
    ) -> None:
        """Save PDF bytes to file.

        Args:
            pdf_bytes: PDF content as bytes
            filepath: Path to save PDF
        """
        try:
            Path(filepath).write_bytes(pdf_bytes)
            logger.info(f"Saved PDF to {filepath}")
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            raise
