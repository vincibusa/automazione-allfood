"""PDF generation service for articles - Robust version."""

import io
import base64
import logging
import re
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from models.schemas import Article

logger = logging.getLogger(__name__)


class ArticlePDF(FPDF):
    """Custom PDF class for articles with AllFoodSicily branding."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(left=20, top=20, right=20)

    def header(self):
        """PDF header with AllFoodSicily branding."""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(180, 50, 50)
        self.cell(0, 10, 'ALLFOODSICILY', align='C', ln=True)

        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, datetime.now().strftime('%d %B %Y'), align='C', ln=True)

        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y() + 2, 190, self.get_y() + 2)
        self.ln(8)

    def footer(self):
        """PDF footer."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Generato da AllFoodSicily AI', align='C')


class PDFGenerator:
    """Service for generating article PDFs with robust error handling."""

    # Characters to replace for PDF compatibility
    UNICODE_REPLACEMENTS = {
        '\u2018': "'",   # Left single quote
        '\u2019': "'",   # Right single quote
        '\u201C': '"',   # Left double quote
        '\u201D': '"',   # Right double quote
        '\u2013': '-',   # En dash
        '\u2014': '-',   # Em dash
        '\u2026': '...',  # Ellipsis
        '\u00A0': ' ',   # Non-breaking space
        '\u200B': '',    # Zero-width space
        '\u00AB': '"',   # Left-pointing double angle quote
        '\u00BB': '"',   # Right-pointing double angle quote
        '\u2022': '-',   # Bullet
        '\u2032': "'",   # Prime
        '\u2033': '"',   # Double prime
        '\u00B0': ' gradi ',  # Degree symbol
        '\u20AC': 'EUR',  # Euro sign
        '\u00E0': 'a',   # a with grave
        '\u00E8': 'e',   # e with grave
        '\u00E9': 'e',   # e with acute
        '\u00EC': 'i',   # i with grave
        '\u00F2': 'o',   # o with grave
        '\u00F9': 'u',   # u with grave
    }

    def __init__(self):
        """Initialize PDF generator."""
        logger.info("Initialized PDF generator")

    def generate_article_pdf(
        self,
        article: Article,
        include_image: bool = True,
        include_sources: bool = True
    ) -> bytes:
        """Generate PDF for an article with robust error handling.

        Args:
            article: Article to convert to PDF
            include_image: Whether to include the generated image
            include_sources: Whether to include sources list

        Returns:
            PDF as bytes
        """
        logger.info(f"Generating PDF for article: {article.title[:50]}...")

        try:
            pdf = ArticlePDF()
            pdf.add_page()

            # Add image if available (with error handling)
            if include_image and article.image_base64:
                self._safe_add_image(pdf, article.image_base64)

            # Add title
            self._add_title(pdf, article.title)

            # Add metadata
            self._add_metadata(pdf, article)

            # Add content
            self._add_content(pdf, article.content)

            # Add sources
            if include_sources and article.topic.fonti:
                self._add_sources(pdf, article.topic.fonti)

            # Output to bytes
            pdf_bytes = pdf.output()
            logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")
            return bytes(pdf_bytes)

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            # Return a minimal error PDF
            return self._generate_error_pdf(article.title, str(e))

    def _safe_text(self, text: str, max_length: Optional[int] = None) -> str:
        """Make text safe for PDF rendering.

        Args:
            text: Input text
            max_length: Optional maximum length

        Returns:
            Safe text for PDF
        """
        if not text:
            return ""

        # Replace known Unicode characters
        for unicode_char, replacement in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, replacement)

        # Remove any remaining non-latin1 characters
        try:
            text.encode('latin-1')
        except UnicodeEncodeError:
            # Keep only ASCII and basic latin characters
            cleaned = []
            for char in text:
                try:
                    char.encode('latin-1')
                    cleaned.append(char)
                except UnicodeEncodeError:
                    cleaned.append(' ')  # Replace with space
            text = ''.join(cleaned)

        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length - 3] + '...'

        return text

    def _safe_add_image(self, pdf: FPDF, image_base64: str) -> None:
        """Add image to PDF with error handling.

        Args:
            pdf: FPDF instance
            image_base64: Base64 encoded image
        """
        try:
            # Decode base64
            image_bytes = base64.b64decode(image_base64)

            # Validate image with PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            # Calculate dimensions
            page_width = pdf.w - 2 * pdf.l_margin
            aspect_ratio = image.height / image.width
            img_width = min(page_width, 170)  # Max 170mm
            img_height = img_width * aspect_ratio

            # Limit height
            if img_height > 90:
                img_height = 90
                img_width = img_height / aspect_ratio

            # Center image
            x_offset = (pdf.w - img_width) / 2

            # Save to BytesIO for FPDF
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)

            pdf.image(img_buffer, x=x_offset, w=img_width, h=img_height)
            pdf.ln(8)

            logger.info(f"Added image: {img_width:.1f}x{img_height:.1f}mm")

        except Exception as e:
            logger.warning(f"Could not add image: {e}")
            # Continue without image

    def _add_title(self, pdf: FPDF, title: str) -> None:
        """Add title to PDF.

        Args:
            pdf: FPDF instance
            title: Article title
        """
        safe_title = self._safe_text(title, max_length=200)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, safe_title, align='L')
        pdf.ln(3)

    def _add_metadata(self, pdf: FPDF, article: Article) -> None:
        """Add metadata line to PDF.

        Args:
            pdf: FPDF instance
            article: Article object
        """
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)

        metadata_parts = [f"{article.word_count} parole"]

        if article.topic.keywords:
            keywords = [self._safe_text(k, 20) for k in article.topic.keywords[:3]]
            metadata_parts.append(', '.join(keywords))

        metadata = ' | '.join(metadata_parts)
        pdf.cell(0, 5, metadata, ln=True)
        pdf.ln(5)

    def _add_content(self, pdf: FPDF, content: str) -> None:
        """Add article content to PDF.

        Args:
            pdf: FPDF instance
            content: Article content (markdown)
        """
        # Clean and normalize content
        clean_content = self._clean_markdown(content)

        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(40, 40, 40)

        # Split into paragraphs
        paragraphs = clean_content.split('\n\n')

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Ensure paragraph isn't too long without spaces
            safe_para = self._safe_text(para)

            # Break very long words
            safe_para = self._break_long_words(safe_para, max_word_length=50)

            if safe_para:
                try:
                    pdf.multi_cell(0, 6, safe_para)
                    pdf.ln(3)
                except Exception as e:
                    logger.warning(f"Could not add paragraph: {e}")
                    continue

    def _add_sources(self, pdf: FPDF, fonti: List[str]) -> None:
        """Add sources section to PDF.

        Args:
            pdf: FPDF instance
            fonti: List of source URLs
        """
        # Check if we need a new page
        if pdf.get_y() > 250:
            pdf.add_page()

        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, 'FONTI:', ln=True)

        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 120)

        for fonte in fonti[:10]:  # Max 10 sources
            # Clean and truncate URL
            safe_url = self._safe_text(fonte, max_length=70)
            if safe_url:
                try:
                    pdf.cell(0, 5, f"- {safe_url}", ln=True)
                except Exception as e:
                    logger.warning(f"Could not add source: {e}")
                    continue

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown formatting for plain text PDF.

        Args:
            text: Markdown text

        Returns:
            Cleaned plain text
        """
        if not text:
            return ""

        # First normalize text
        text = self._safe_text(text)

        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove bold/italic markers
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)

        # Convert links to text only
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove list markers
        text = re.sub(r'^\s*[-*+]\s+', '- ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Clean up code blocks
        text = re.sub(r'```[a-z]*\n?', '', text)

        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Clean up multiple spaces
        text = re.sub(r' {2,}', ' ', text)

        return text.strip()

    def _break_long_words(self, text: str, max_word_length: int = 50) -> str:
        """Break very long words to prevent PDF rendering issues.

        Args:
            text: Input text
            max_word_length: Maximum word length before breaking

        Returns:
            Text with long words broken
        """
        words = text.split()
        result = []

        for word in words:
            if len(word) > max_word_length:
                # Break long word with hyphens
                chunks = [word[i:i+max_word_length-1] + '-'
                          for i in range(0, len(word), max_word_length-1)]
                # Remove trailing hyphen from last chunk
                if chunks:
                    chunks[-1] = chunks[-1].rstrip('-')
                result.extend(chunks)
            else:
                result.append(word)

        return ' '.join(result)

    def _generate_error_pdf(self, title: str, error: str) -> bytes:
        """Generate a minimal error PDF when main generation fails.

        Args:
            title: Original article title
            error: Error message

        Returns:
            Error PDF as bytes
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, 'AllFoodSicily', ln=True, align='C')
            pdf.ln(10)
            pdf.set_font('Helvetica', '', 12)
            pdf.multi_cell(0, 8, f"Errore nella generazione del PDF per:\n{title[:100]}")
            pdf.ln(5)
            pdf.set_font('Helvetica', 'I', 10)
            pdf.multi_cell(0, 6, f"Dettaglio: {error[:200]}")
            return bytes(pdf.output())
        except Exception:
            # Absolute fallback
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(0, 10, 'PDF generation error', ln=True)
            return bytes(pdf.output())

    def save_pdf_to_file(self, pdf_bytes: bytes, filepath: str) -> None:
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
