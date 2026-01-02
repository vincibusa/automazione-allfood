"""Main entry point for AllFoodSicily bot and workflow."""

import sys
import asyncio
import argparse
import logging
from datetime import time as dt_time

import pytz

from config.settings import settings
from services.telegram_bot import TelegramBotService
from utils.logger import logger

logger = logging.getLogger(__name__)


async def scheduled_workflow_job(context) -> None:
    """Job callback for scheduled workflow execution at 9:00.

    This is called by the Telegram bot's JobQueue.

    Args:
        context: Job context from Telegram
    """
    logger.info("=" * 60)
    logger.info("🕐 Scheduled workflow starting (09:00)")
    logger.info("=" * 60)

    try:
        # Import workflow orchestrator
        from workflow.search_phase import execute_search_phase
        from workflow.scrape_phase import execute_scrape_phase
        from workflow.analysis_phase import execute_analysis_phase
        from workflow.generation_phase import execute_generation_phase
        from workflow.output_phase import execute_output_phase
        from models.schemas import WorkflowResult
        from config.sources import ALL_SITES
        from datetime import datetime

        start_time = datetime.now()

        # Execute workflow phases
        logger.info("🔍 Phase 1: Search")
        search_results = execute_search_phase(days_back=7)

        logger.info("🕷️  Phase 2: Scrape")
        scraped_content = execute_scrape_phase()

        logger.info("🤖 Phase 3: Analysis")
        topics = execute_analysis_phase(search_results, scraped_content)

        if not topics:
            logger.warning("⚠️  No topics selected, ending workflow")
            result = WorkflowResult(
                articles=[],
                docs=[],
                sources_monitored=len(ALL_SITES),
                execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message="No topics selected from analysis"
            )
        else:
            logger.info("✍️  Phase 4: Generation")
            articles = execute_generation_phase(topics)

            logger.info("📄 Phase 5: Output (PDF)")
            pdf_results = execute_output_phase(articles)

            result = WorkflowResult(
                articles=articles,
                docs=[],  # No more Google Docs
                sources_monitored=len(ALL_SITES),
                execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )

        # Send results via Telegram
        bot_service = TelegramBotService()
        await bot_service.send_workflow_summary(result)

        logger.info(f"✅ Scheduled workflow completed: {len(result.articles)} articles")

    except Exception as e:
        logger.error(f"❌ Scheduled workflow failed: {e}", exc_info=True)

        # Send error notification
        bot_service = TelegramBotService()
        bot_service.send_error_notification(f"Errore workflow automatico: {str(e)}")


async def run_workflow_once() -> None:
    """Execute workflow once and exit (--now flag).

    This is used for immediate execution instead of running the bot.
    """
    logger.info("🚀 Executing workflow immediately (--now)")

    try:
        from workflow.search_phase import execute_search_phase
        from workflow.scrape_phase import execute_scrape_phase
        from workflow.analysis_phase import execute_analysis_phase
        from workflow.generation_phase import execute_generation_phase
        from workflow.output_phase import execute_output_phase
        from models.schemas import WorkflowResult
        from config.sources import ALL_SITES
        from datetime import datetime

        start_time = datetime.now()

        # Execute workflow phases
        logger.info("=" * 60)
        logger.info("🔍 PHASE 1: Search")
        logger.info("=" * 60)
        search_results = execute_search_phase(days_back=7)

        logger.info("")
        logger.info("=" * 60)
        logger.info("🕷️  PHASE 2: Scrape")
        logger.info("=" * 60)
        scraped_content = execute_scrape_phase()

        logger.info("")
        logger.info("=" * 60)
        logger.info("🤖 PHASE 3: Analysis")
        logger.info("=" * 60)
        topics = execute_analysis_phase(search_results, scraped_content)

        if not topics:
            logger.warning("⚠️  No topics selected, ending workflow")
            result = WorkflowResult(
                articles=[],
                docs=[],
                sources_monitored=len(ALL_SITES),
                execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message="No topics selected from analysis"
            )
            sys.exit(1)

        logger.info("")
        logger.info("=" * 60)
        logger.info("✍️  PHASE 4: Generation")
        logger.info("=" * 60)
        articles = execute_generation_phase(topics)

        logger.info("")
        logger.info("=" * 60)
        logger.info("📄 PHASE 5: Output (PDF)")
        logger.info("=" * 60)
        pdf_results = execute_output_phase(articles)

        result = WorkflowResult(
            articles=articles,
            docs=[],  # No more Google Docs
            sources_monitored=len(ALL_SITES),
            execution_timestamp=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            success=True
        )

        # Send results
        logger.info("")
        logger.info("📱 Sending results to Telegram...")
        bot_service = TelegramBotService()
        await bot_service.send_workflow_summary(result)

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Workflow completed successfully")
        logger.info(f"📝 Articles: {len(articles)}")
        logger.info(f"🔗 Sources: {len(ALL_SITES)}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}", exc_info=True)
        sys.exit(1)


async def run_bot_with_scheduler() -> None:
    """Run Telegram bot with integrated daily scheduler.

    This is the main mode of operation. The bot:
    - Listens for commands and messages
    - Runs scheduled workflow at 9:00 AM every day
    """
    logger.info("=" * 60)
    logger.info("🤖 Starting AllFoodSicily Bot with Scheduler")
    logger.info("=" * 60)

    # Build bot application
    bot_service = TelegramBotService()
    app = bot_service.build_application()

    # Configure scheduled job at 09:00 Rome time
    logger.info("⏰ Configuring daily scheduler...")
    rome_tz = pytz.timezone(settings.TIMEZONE)
    job_time = dt_time(hour=9, minute=0, tzinfo=rome_tz)

    app.job_queue.run_daily(
        callback=scheduled_workflow_job,
        time=job_time,
        name="daily_workflow"
    )

    logger.info(f"✅ Scheduled daily workflow at 09:00 ({settings.TIMEZONE})")
    logger.info("")
    logger.info("🎯 Bot is now ready!")
    logger.info("   • Listening for commands: /start, /help, /articolo")
    logger.info("   • Accepting natural language requests")
    logger.info("   • Daily workflow scheduled at 09:00")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Run the bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep running until stopped
    try:
        # Sleep indefinitely
        while True:
            await asyncio.sleep(3600)  # Check every hour
    except asyncio.CancelledError:
        logger.info("🛑 Bot stopping...")
    finally:
        # Graceful shutdown
        logger.info("🔄 Shutting down gracefully...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        logger.info("✅ Shutdown complete")


def validate_settings() -> bool:
    """Validate that all required settings are present.

    Returns:
        True if valid, False otherwise
    """
    missing = settings.validate()
    if missing:
        logger.error("❌ Missing required settings:")
        for setting in missing:
            logger.error(f"   • {setting}")
        logger.error("")
        logger.error("Please check your .env file and ensure all required variables are set.")
        return False

    logger.info("✅ Settings validation passed")
    return True


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="AllFoodSicily - Automated Food Content Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                 Run bot with scheduler (default)
  %(prog)s --now           Execute workflow immediately and exit
  %(prog)s --validate      Validate settings and exit
"""
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Execute workflow immediately instead of running bot"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate settings and exit"
    )

    args = parser.parse_args()

    # Validate settings first
    if not validate_settings():
        sys.exit(1)

    # Handle validate flag
    if args.validate:
        logger.info("")
        logger.info("All settings are configured correctly!")
        sys.exit(0)

    # Execute workflow or run bot
    try:
        if args.now:
            # Run workflow once
            asyncio.run(run_workflow_once())
        else:
            # Run bot with scheduler (default mode)
            asyncio.run(run_bot_with_scheduler())
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
