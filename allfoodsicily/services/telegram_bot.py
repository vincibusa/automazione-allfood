"""Telegram bot integration for notifications."""

import logging
from typing import List
from datetime import datetime

from telegram import Bot
from telegram.error import TelegramError

from config.settings import settings
from models.schemas import Article, GoogleDocInfo, WorkflowResult
from utils.retry import retry_api_call

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram notification service."""
    
    def __init__(self):
        """Initialize Telegram bot."""
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.chat_id = settings.TELEGRAM_CHAT_ID
        logger.info("Initialized Telegram notifier")
    
    @retry_api_call(max_attempts=3)
    def send_notification(self, message: str) -> bool:
        """Send a notification message.
        
        Args:
            message: Message to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import asyncio
            
            async def _send():
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML'
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
    
    def _convert_markdown_to_telegram(self, text: str) -> str:
        """Convert markdown/HTML to Telegram HTML format.
        
        Args:
            text: Markdown/HTML text
            
        Returns:
            Telegram HTML formatted text
        """
        import re
        
        # Remove markdown headers and convert to bold
        text = re.sub(r'^#+\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # Convert markdown bold to HTML bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        
        # Convert markdown italic to HTML italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
        # Convert markdown links to HTML links
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Remove markdown list markers, keep structure
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _split_message(self, text: str, max_length: int = 4000) -> List[str]:
        """Split long message into chunks respecting Telegram limits.
        
        Args:
            text: Text to split
            max_length: Maximum length per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If single paragraph is too long, split by sentences
                if len(para) > max_length:
                    sentences = para.split('. ')
                    for sent in sentences:
                        if len(current_chunk) + len(sent) + 2 <= max_length:
                            current_chunk += sent + '. '
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sent + '. '
                else:
                    current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def send_article(self, article: Article, doc_info: GoogleDocInfo = None, article_num: int = None) -> bool:
        """Send a single article to Telegram.
        
        Args:
            article: Article to send
            doc_info: Optional Google Doc info
            article_num: Optional article number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import asyncio
            
            async def _send_article():
                # Build article header
                header = f"📝 <b>Articolo {article_num}</b>\n\n" if article_num else "📝 <b>Articolo</b>\n\n"
                header += f"<b>{article.title}</b>\n\n"
                
                if doc_info:
                    header += f"📄 <a href='{doc_info.doc_url}'>Apri su Google Docs</a>\n\n"
                
                header += "━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # Convert content to Telegram format
                content = self._convert_markdown_to_telegram(article.content)
                
                # Combine header and content
                full_message = header + content
                
                # Add footer with metadata
                footer = f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
                footer += f"📊 <i>{article.word_count} parole</i>"
                if article.topic.keywords:
                    footer += f" | 🏷️ <i>{', '.join(article.topic.keywords[:3])}</i>"
                
                full_message += footer
                
                # Split if too long
                chunks = self._split_message(full_message)
                
                # Send all chunks
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        # First chunk
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=chunk,
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        )
                    else:
                        # Continuation chunks
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=f"<i>(continua...)</i>\n\n{chunk}",
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        )
                
                return True
            
            asyncio.run(_send_article())
            logger.info(f"Article '{article.title}' sent to Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Error sending article to Telegram: {str(e)}")
            return False
    
    def send_workflow_summary(self, result: WorkflowResult) -> bool:
        """Send workflow execution summary and all articles.
        
        Args:
            result: Workflow result
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("Preparing workflow summary for Telegram")
        
        try:
            import asyncio
            
            async def _send_all():
                # Build summary message
                emoji_article = "📝"
                emoji_link = "📄"
                emoji_sources = "🔗"
                emoji_time = "⏰"
                emoji_success = "✅"
                emoji_error = "❌"
                
                if result.success:
                    status_emoji = emoji_success
                    status_text = "completato con successo"
                else:
                    status_emoji = emoji_error
                    status_text = f"completato con errori: {result.error_message}"
                
                summary = f"""🍝 <b>Nuove bozze AllFoodSicily pronte!</b>

{status_emoji} <b>Stato:</b> {status_text}

{emoji_article} <b>Articoli generati:</b> {len(result.articles)}

"""
                
                # Add article list with links
                if result.articles:
                    for i, article in enumerate(result.articles, 1):
                        doc = result.docs[i-1] if i <= len(result.docs) else None
                        summary += f"{i}. <b>{article.title}</b>\n"
                        if doc:
                            summary += f"   {emoji_link} <a href='{doc.doc_url}'>Google Doc</a>\n"
                        summary += f"   📊 {article.word_count} parole\n\n"
                
                # Add sources info
                summary += f"{emoji_sources} <b>Fonti monitorate:</b> {result.sources_monitored} siti\n"
                summary += f"{emoji_time} <b>Generato:</b> {result.execution_timestamp}"
                
                # Send summary first
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=summary,
                    parse_mode='HTML'
                )
                
                # Send each article separately
                if result.articles:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text="━━━━━━━━━━━━━━━━━━━━\n📰 <b>ARTICOLI COMPLETI</b>\n━━━━━━━━━━━━━━━━━━━━",
                        parse_mode='HTML'
                    )
                    
                    for i, article in enumerate(result.articles, 1):
                        doc = result.docs[i-1] if i <= len(result.docs) else None
                        
                        # Build article message
                        header = f"📝 <b>Articolo {i}/{len(result.articles)}</b>\n\n"
                        header += f"<b>{article.title}</b>\n\n"
                        
                        if doc:
                            header += f"📄 <a href='{doc.doc_url}'>Apri su Google Docs</a>\n\n"
                        
                        header += "━━━━━━━━━━━━━━━━━━━━\n\n"
                        
                        # Convert content
                        content = self._convert_markdown_to_telegram(article.content)
                        
                        # Combine
                        full_message = header + content
                        
                        # Add footer
                        footer = f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
                        footer += f"📊 <i>{article.word_count} parole</i>"
                        if article.topic.keywords:
                            footer += f" | 🏷️ <i>{', '.join(article.topic.keywords[:3])}</i>"
                        if article.topic.fonti:
                            footer += f"\n🔗 <i>Fonti: {len(article.topic.fonti)} link</i>"
                        
                        full_message += footer
                        
                        # Split if too long
                        chunks = self._split_message(full_message)
                        
                        # Send chunks
                        for chunk_idx, chunk in enumerate(chunks):
                            if chunk_idx == 0:
                                await self.bot.send_message(
                                    chat_id=self.chat_id,
                                    text=chunk,
                                    parse_mode='HTML',
                                    disable_web_page_preview=True
                                )
                            else:
                                await self.bot.send_message(
                                    chat_id=self.chat_id,
                                    text=f"<i>(continua articolo {i}...)</i>\n\n{chunk}",
                                    parse_mode='HTML',
                                    disable_web_page_preview=True
                                )
                        
                        # Small delay between articles
                        import asyncio as aio
                        await aio.sleep(0.5)
                
                return True
            
            asyncio.run(_send_all())
            logger.info("Workflow summary and articles sent to Telegram successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending workflow summary to Telegram: {str(e)}")
            return False
    
    def send_error_notification(self, error_message: str) -> bool:
        """Send error notification.
        
        Args:
            error_message: Error message to send
            
        Returns:
            True if successful, False otherwise
        """
        message = f"""❌ <b>Errore nel workflow AllFoodSicily</b>

{error_message}

⏰ <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        return self.send_notification(message)

