"""Script di test per verificare la configurazione Telegram."""

import sys
import asyncio
from config.settings import settings
from services.telegram_bot import TelegramNotifier

def test_telegram():
    """Test invio messaggio Telegram."""
    
    print("🧪 Test configurazione Telegram...")
    print()
    
    # Verifica configurazione
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ ERRORE: TELEGRAM_BOT_TOKEN non configurato")
        sys.exit(1)
    
    if not settings.TELEGRAM_CHAT_ID:
        print("❌ ERRORE: TELEGRAM_CHAT_ID non configurato")
        sys.exit(1)
    
    print(f"✅ Token configurato: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"✅ Chat ID configurato: {settings.TELEGRAM_CHAT_ID}")
    print()
    
    # Test invio
    print("📤 Invio messaggio di test...")
    
    try:
        notifier = TelegramNotifier()
        
        # Usa asyncio per chiamare il metodo asincrono
        async def send_test():
            return await notifier.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text="✅ <b>Test AllFoodSicily Bot</b>\n\nIl bot Telegram è configurato correttamente! 🎉",
                parse_mode='HTML'
            )
        
        result = asyncio.run(send_test())
        
        if result:
            print("✅ Messaggio inviato con successo!")
            print("📱 Controlla Telegram per vedere il messaggio")
        else:
            print("❌ Errore nell'invio del messaggio")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_telegram()

