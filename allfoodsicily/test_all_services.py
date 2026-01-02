"""Script per testare tutte le configurazioni dei servizi."""

import sys
from config.settings import settings

def test_configuration():
    """Testa tutte le configurazioni."""
    
    print("🧪 Test Configurazione AllFoodSicily Workflow")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # Test Telegram
    print("📱 Telegram Bot...")
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        print("   ✅ Configurato")
        try:
            from services.telegram_bot import TelegramNotifier
            notifier = TelegramNotifier()
            print("   ✅ Import riuscito")
        except Exception as e:
            errors.append(f"Telegram: {str(e)}")
            print(f"   ❌ Errore: {str(e)}")
    else:
        errors.append("Telegram: Token o Chat ID mancanti")
        print("   ❌ Non configurato")
    print()
    
    # Test Google Docs
    print("📄 Google Docs...")
    from pathlib import Path
    service_account_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_FILE)
    if service_account_path.exists():
        print("   ✅ Service Account trovato")
        try:
            from services.google_docs import GoogleDocsService
            docs_service = GoogleDocsService()
            print("   ✅ Connessione riuscita")
        except Exception as e:
            errors.append(f"Google Docs: {str(e)}")
            print(f"   ❌ Errore: {str(e)}")
    else:
        errors.append("Google Docs: service_account.json non trovato")
        print("   ❌ Service Account non trovato")
    print()
    
    # Test Gemini
    print("🤖 Google Gemini...")
    if settings.GEMINI_API_KEY:
        print("   ✅ API Key configurata")
        try:
            from services.gemini_client import GeminiClient
            gemini = GeminiClient()
            print("   ✅ Client inizializzato")
        except Exception as e:
            errors.append(f"Gemini: {str(e)}")
            print(f"   ❌ Errore: {str(e)}")
    else:
        warnings.append("Gemini: API Key non configurata")
        print("   ⚠️  API Key non configurata")
    print()
    
    # Test Gemini Search/Scrape (sostituisce Firecrawl)
    print("🔍 Gemini Search & Scrape...")
    if settings.GEMINI_API_KEY:
        print("   ✅ API Key configurata")
        try:
            from services.gemini_search import GeminiSearch
            searcher = GeminiSearch()
            print("   ✅ Client inizializzato")
        except Exception as e:
            errors.append(f"Gemini Search: {str(e)}")
            print(f"   ❌ Errore: {str(e)}")
    else:
        warnings.append("Gemini: API Key non configurata")
        print("   ⚠️  API Key non configurata")
    print()
    
    # Riepilogo
    print("=" * 60)
    if errors:
        print("❌ ERRORI TROVATI:")
        for error in errors:
            print(f"   - {error}")
        print()
        return False
    else:
        print("✅ Tutte le configurazioni principali sono OK!")
        if warnings:
            print()
            print("⚠️  AVVISI:")
            for warning in warnings:
                print(f"   - {warning}")
        print()
        print("🚀 Pronto per eseguire il workflow!")
        return True

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1)

