"""Interactive Telegram bot with command handling and scheduled jobs."""

import re
import logging
import asyncio
from typing import Optional, List
from datetime import datetime
from io import BytesIO

from telegram import Update, Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError

from config.settings import settings
from models.schemas import Article, WorkflowResult
from services.pdf_generator import PDFGenerator
from utils.retry import retry_api_call

logger = logging.getLogger(__name__)

# Patterns for natural language article requests
ARTICLE_PATTERNS = [
    r"scrivi\s+(?:un\s+)?(?:articolo|pezzo)\s+(?:su|riguardo|circa)\s+(.+)",
    r"fammi\s+(?:un\s+)?(?:articolo|pezzo)\s+(?:su|riguardo|per)\s+(.+)",
    r"genera\s+(?:un\s+)?(?:articolo|contenuto)\s+(?:su|per)\s+(.+)",
    r"crea\s+(?:un\s+)?(?:articolo|pezzo)\s+(?:su|riguardo)\s+(.+)",
    r"vorrei\s+(?:un\s+)?(?:articolo|pezzo)\s+(?:su|riguardo)\s+(.+)",
    r"puoi\s+scrivere\s+(?:un\s+)?(?:articolo|qualcosa)\s+(?:su|riguardo)\s+(.+)",
]


class TelegramBotService:
    """Interactive Telegram bot service with command and message handling."""

    def __init__(self):
        """Initialize Telegram bot service."""
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.pdf_generator = PDFGenerator()
        self.application: Optional[Application] = None
        logger.info("Initialized Telegram bot service")

    def extract_topic_from_message(self, text: str) -> Optional[str]:
        """Extract article topic from natural language message.

        Args:
            text: User message

        Returns:
            Extracted topic or None if no match
        """
        text_lower = text.lower().strip()

        for pattern in ARTICLE_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                # Remove trailing punctuation
                topic = topic.rstrip('.,!?;')
                return topic

        return None

    async def handle_start_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start and /help commands."""
        welcome_message = """🍝 **Ciao! Sono il bot di AllFoodSicily.**

Posso generare articoli su argomenti food siciliani per te!

**Comandi disponibili:**
• `/articolo <argomento>` - Genera un articolo su un argomento specifico
• `/help` - Mostra questo messaggio

**Oppure scrivi in linguaggio naturale:**
• "Scrivi un articolo sulla cassata siciliana"
• "Fammi un pezzo sui cannoli di Piana degli Albanesi"
• "Vorrei un articolo sui pistacchi di Bronte"

🕐 **Workflow automatico:**
Ogni mattina alle 9:00 genero automaticamente articoli sulle ultime novità food siciliane.

Tutti gli articoli ti vengono inviati come file PDF completi di testo, immagini e fonti!
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def handle_articolo_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /articolo <topic> command.

        Args:
            update: Telegram update
            context: Handler context
        """
        if not context.args:
            await update.message.reply_text(
                "❌ **Uso corretto:**\n"
                "`/articolo <argomento>`\n\n"
                "**Esempio:**\n"
                "`/articolo arancini di Catania`",
                parse_mode='Markdown'
            )
            return

        topic = ' '.join(context.args)
        await self._generate_and_send_article(update, topic)

    async def handle_natural_language(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle natural language messages.

        Args:
            update: Telegram update
            context: Handler context
        """
        text = update.message.text

        topic = self.extract_topic_from_message(text)

        if topic:
            await self._generate_and_send_article(update, topic)
        else:
            # Message not recognized as article request
            await update.message.reply_text(
                "🤔 Non ho capito la richiesta. Prova con:\n\n"
                "• `/articolo <argomento>`\n"
                "• 'Scrivi un articolo su...'\n"
                "• 'Fammi un pezzo su...'\n\n"
                "Oppure usa `/help` per vedere tutti i comandi.",
                parse_mode='Markdown'
            )

    async def _generate_and_send_article(
        self,
        update: Update,
        topic: str
    ) -> None:
        """Generate article for topic and send as PDF.

        Args:
            update: Telegram update
            topic: Article topic
        """
        chat_id = update.effective_chat.id

        # Send "working" message
        status_msg = await update.message.reply_text(
            f"🔄 **Sto lavorando...**\n\n"
            f"Genero un articolo su: *{topic}*\n\n"
            f"Questo richiederà 1-2 minuti...\n"
            f"✍️ Ricerca fonti\n"
            f"📝 Scrittura articolo\n"
            f"🎨 Creazione immagine\n"
            f"📄 Generazione PDF",
            parse_mode='Markdown'
        )

        try:
            # Import here to avoid circular imports
            from workflow.manual_workflow import execute_manual_workflow

            # Execute manual workflow
            logger.info(f"Executing manual workflow for topic: {topic}")
            article, pdf_bytes = await execute_manual_workflow(topic)

            # Delete status message
            await status_msg.delete()

            # Send PDF
            filename = self._sanitize_filename(f"AllFoodSicily_{topic}.pdf")

            caption = (
                f"📝 **{article.title}**\n\n"
                f"📊 {article.word_count} parole\n"
                f"🏷️ {', '.join(article.topic.keywords[:3])}\n"
                f"🔗 {len(article.topic.fonti)} fonti"
            )

            await update.message.reply_document(
                document=BytesIO(pdf_bytes),
                filename=filename,
                caption=caption,
                parse_mode='Markdown'
            )

            logger.info(f"✅ Article PDF sent successfully: {article.title}")

        except Exception as e:
            logger.error(f"❌ Error generating article: {e}", exc_info=True)
            await status_msg.edit_text(
                f"❌ **Errore durante la generazione**\n\n"
                f"Si è verificato un errore:\n"
                f"`{str(e)[:100]}`\n\n"
                f"Riprova o contatta il supporto.",
                parse_mode='Markdown'
            )

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe download.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove special characters
        filename = re.sub(r'[^\w\-.]', '', filename)
        # Limit length
        if len(filename) > 50:
            name, ext = filename.rsplit('.', 1)
            filename = name[:46] + '.' + ext
        return filename

    async def send_pdf_article(
        self,
        article: Article,
        pdf_bytes: bytes,
        caption: Optional[str] = None
    ) -> bool:
        """Send article PDF to configured chat.

        Args:
            article: Article that was generated
            pdf_bytes: PDF content as bytes
            caption: Optional caption for the document

        Returns:
            True if successful
        """
        if not self.application:
            # Use low-level bot if application not running
            bot = Bot(token=self.token)
            async with bot:
                return await self._send_document(bot, article, pdf_bytes, caption)
        else:
            return await self._send_document(
                self.application.bot, article, pdf_bytes, caption
            )

    async def _send_document(
        self,
        bot: Bot,
        article: Article,
        pdf_bytes: bytes,
        caption: Optional[str] = None
    ) -> bool:
        """Internal method to send document.

        Args:
            bot: Bot instance
            article: Article object
            pdf_bytes: PDF bytes
            caption: Optional caption

        Returns:
            True if successful
        """
        try:
            filename = self._sanitize_filename(f"AllFoodSicily_{article.title}.pdf")

            if not caption:
                caption = (
                    f"📝 **{article.title}**\n\n"
                    f"📊 {article.word_count} parole\n"
                    f"🏷️ {', '.join(article.topic.keywords[:3])}"
                )

            await bot.send_document(
                chat_id=self.chat_id,
                document=BytesIO(pdf_bytes),
                filename=filename,
                caption=caption,
                parse_mode='Markdown'
            )

            logger.info(f"✅ PDF sent successfully: {article.title}")
            return True

        except TelegramError as e:
            logger.error(f"❌ Error sending PDF: {e}")
            return False

    async def send_workflow_summary(self, result: WorkflowResult) -> bool:
        """Send workflow summary with all articles as PDFs.

        Args:
            result: Workflow result with articles

        Returns:
            True if successful
        """
        try:
            bot = Bot(token=self.token)

            async with bot:
                # Send summary message first
                summary = self._build_summary_message(result)
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=summary,
                    parse_mode='Markdown'
                )

                # Generate and send each article as PDF
                for i, article in enumerate(result.articles, 1):
                    logger.info(f"Generating PDF {i}/{len(result.articles)}: {article.title}")

                    pdf_bytes = self.pdf_generator.generate_article_pdf(
                        article,
                        include_image=(article.image_base64 is not None),
                        include_sources=True
                    )

                    filename = self._sanitize_filename(f"Articolo_{i}_{article.title}.pdf")

                    caption = (
                        f"📝 **Articolo {i}/{len(result.articles)}**\n\n"
                        f"**{article.title}**\n\n"
                        f"📊 {article.word_count} parole"
                    )

                    await bot.send_document(
                        chat_id=self.chat_id,
                        document=BytesIO(pdf_bytes),
                        filename=filename,
                        caption=caption,
                        parse_mode='Markdown'
                    )

                    # Small delay between sends
                    await asyncio.sleep(0.5)

            logger.info(f"✅ Workflow summary and {len(result.articles)} PDFs sent successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending workflow summary: {e}", exc_info=True)
            return False

    def _build_summary_message(self, result: WorkflowResult) -> str:
        """Build summary message for workflow result.

        Args:
            result: Workflow result

        Returns:
            Formatted summary message
        """
        if result.success:
            status_emoji = "✅"
            status_text = "completato con successo"
        else:
            status_emoji = "❌"
            status_text = f"completato con errori:\n`{result.error_message}`"

        summary = f"""🍝 **Workflow Automatico AllFoodSicily**

{status_emoji} **Stato:** {status_text}

📝 **Articoli generati:** {len(result.articles)}
🔗 **Fonti monitorate:** {result.sources_monitored}
🕐 **Timestamp:** {result.execution_timestamp}

"""

        if result.articles:
            summary += "**📋 Articoli:**\n"
            for i, article in enumerate(result.articles, 1):
                summary += f"{i}. {article.title} ({article.word_count} parole)\n"

        summary += "\n📄 I PDF completi seguono..."

        return summary

    @retry_api_call(max_attempts=3)
    def send_notification(self, message: str) -> bool:
        """Send a simple text notification (legacy method).

        Args:
            message: Message to send

        Returns:
            True if successful
        """
        try:
            async def _send():
                bot = Bot(token=self.token)
                async with bot:
                    await bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )

            asyncio.run(_send())
            logger.info("Telegram notification sent successfully")
            return True

        except TelegramError as e:
            logger.error(f"Error sending Telegram notification: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {str(e)}")
            return False

    def send_error_notification(self, error_message: str) -> bool:
        """Send error notification.

        Args:
            error_message: Error message to send

        Returns:
            True if successful
        """
        message = f"""❌ **Errore nel workflow AllFoodSicily**

{error_message}

🕐 **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        return self.send_notification(message)

    def build_application(self) -> Application:
        """Build and configure the Telegram application with handlers.

        Returns:
            Configured Application ready to run
        """
        logger.info("Building Telegram Application...")

        self.application = (
            ApplicationBuilder()
            .token(self.token)
            .build()
        )

        # Add command handlers
        self.application.add_handler(
            CommandHandler("start", self.handle_start_command)
        )
        self.application.add_handler(
            CommandHandler("help", self.handle_start_command)
        )
        self.application.add_handler(
            CommandHandler("articolo", self.handle_articolo_command)
        )

        # Add natural language message handler
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_natural_language
            )
        )

        logger.info("✅ Telegram Application built with handlers:")
        logger.info("   - /start, /help: Welcome message")
        logger.info("   - /articolo <topic>: Generate article")
        logger.info("   - Natural language: Article requests")

        return self.application
