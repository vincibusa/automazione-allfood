"""Main entry point for AllFoodSicily workflow."""

import sys
import argparse
import schedule
import time
from datetime import datetime
from typing import Optional

from config.settings import settings
from config.sources import ALL_SITES
from models.schemas import WorkflowResult
from workflow.search_phase import execute_search_phase
from workflow.scrape_phase import execute_scrape_phase
from workflow.analysis_phase import execute_analysis_phase
from workflow.generation_phase import execute_generation_phase
from workflow.output_phase import execute_output_phase
from services.telegram_bot import TelegramNotifier
from utils.logger import logger


def validate_settings() -> bool:
    """Validate that all required settings are present.
    
    Returns:
        True if valid, False otherwise
    """
    missing = settings.validate()
    if missing:
        logger.error(f"Missing required settings: {', '.join(missing)}")
        logger.error("Please check your .env file")
        return False
    return True


def execute_workflow() -> WorkflowResult:
    """Execute the complete workflow.
    
    Returns:
        WorkflowResult with execution details
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting AllFoodSicily Workflow")
    logger.info("=" * 60)
    
    try:
        # Phase 1: Search for food news (sempre Gemini)
        logger.info("")
        logger.info("🔍 FASE 1: Ricerca novità food Sicilia")
        logger.info("-" * 60)
        search_results = execute_search_phase(days_back=7)
        logger.info(f"✅ Fase 1 completata: {len(search_results)} risultati trovati")
        logger.info("")
        
        # Phase 2: Scrape monitored sites
        logger.info("🕷️  FASE 2: Scraping siti monitorati")
        logger.info("-" * 60)
        scraped_content = execute_scrape_phase()
        logger.info(f"✅ Fase 2 completata: {len(scraped_content)} siti scrapati")
        logger.info("")
        
        # Phase 3: Analyze and select topics
        logger.info("🤖 FASE 3: Analisi e selezione topic")
        logger.info("-" * 60)
        topics = execute_analysis_phase(search_results, scraped_content)
        logger.info(f"✅ Fase 3 completata: {len(topics)} topic selezionati")
        logger.info("")
        
        if not topics:
            logger.warning("No topics selected, ending workflow")
            return WorkflowResult(
                articles=[],
                docs=[],
                sources_monitored=len(ALL_SITES),
                execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message="No topics selected from analysis"
            )
        
        # Phase 4: Generate articles and images
        logger.info("✍️  FASE 4: Generazione articoli e immagini")
        logger.info("-" * 60)
        articles = execute_generation_phase(topics)
        logger.info(f"✅ Fase 4 completata: {len(articles)} articoli generati")
        logger.info("")
        
        if not articles:
            logger.warning("⚠️  Nessun articolo generato, terminando workflow")
            return WorkflowResult(
                articles=[],
                docs=[],
                sources_monitored=len(ALL_SITES),
                execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message="No articles generated"
            )
        
        # Phase 5: Save to Google Docs
        logger.info("📄 FASE 5: Salvataggio su Google Docs e notifica Telegram")
        logger.info("-" * 60)
        docs = execute_output_phase(articles)
        logger.info(f"✅ Fase 5 completata: {len(docs)} documenti creati")
        logger.info("")
        
        # Prepare result
        result = WorkflowResult(
            articles=articles,
            docs=docs,
            sources_monitored=len(ALL_SITES),
            execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            success=True
        )
        
        # Send Telegram notification
        logger.info("📱 Invio notifica Telegram...")
        try:
            telegram_notifier = TelegramNotifier()
            telegram_notifier.send_workflow_summary(result)
            logger.info("✅ Notifica Telegram inviata")
        except Exception as e:
            logger.error(f"Errore invio notifica Telegram: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"🎉 WORKFLOW COMPLETATO CON SUCCESSO!")
        logger.info(f"⏱️  Durata totale: {duration:.1f} secondi ({duration/60:.1f} minuti)")
        logger.info(f"📝 Articoli generati: {len(articles)}")
        logger.info(f"📄 Documenti Google Docs creati: {len(docs)}")
        logger.info(f"🔗 Fonti monitorate: {len(ALL_SITES)}")
        logger.info("=" * 60)
        
        return result
        
    except Exception as e:
        error_message = f"Workflow failed: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        # Send error notification
        try:
            telegram_notifier = TelegramNotifier()
            telegram_notifier.send_error_notification(error_message)
        except Exception as notify_error:
            logger.error(f"Failed to send error notification: {str(notify_error)}")
        
        return WorkflowResult(
            articles=[],
            docs=[],
            sources_monitored=len(ALL_SITES),
            execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            success=False,
            error_message=error_message
        )


def run_scheduler():
    """Run the workflow scheduler."""
    logger.info(f"Scheduler started - Daily execution at {settings.DAILY_EXECUTION_HOUR}:00")
    
    # Schedule daily execution
    schedule.every().day.at(f"{settings.DAILY_EXECUTION_HOUR:02d}:00").do(execute_workflow)
    
    # Run scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AllFoodSicily Workflow Automation")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Execute workflow immediately instead of scheduling"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate settings and exit"
    )
    
    args = parser.parse_args()
    
    # Validate settings
    if not validate_settings():
        sys.exit(1)
    
    if args.validate:
        logger.info("Settings validation passed")
        sys.exit(0)
    
    # Execute workflow
    if args.now:
        logger.info("Executing workflow immediately (--now flag)")
        result = execute_workflow()
        sys.exit(0 if result.success else 1)
    else:
        # Run scheduler
        logger.info("Starting scheduler mode")
        try:
            run_scheduler()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            sys.exit(0)


if __name__ == "__main__":
    main()

