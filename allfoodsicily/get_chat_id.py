"""Script helper per ottenere il Chat ID di Telegram."""

import sys
import requests
from config.settings import settings

def get_chat_id():
    """Ottieni il Chat ID dal bot Telegram."""
    
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ ERRORE: TELEGRAM_BOT_TOKEN non configurato nel .env")
        print("Aggiungi il token nel file .env:")
        print("TELEGRAM_BOT_TOKEN=8561234151:AAHZ7xFRfF1hUWJyRZkxTZRWcjDUm9MvOGE")
        sys.exit(1)
    
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    print("🔍 Cercando messaggi dal bot...")
    print(f"📱 Assicurati di aver inviato un messaggio a @allfoodsicilynotify_bot su Telegram")
    print()
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get("ok"):
            print(f"❌ Errore API Telegram: {data.get('description', 'Unknown error')}")
            sys.exit(1)
        
        results = data.get("result", [])
        
        if not results:
            print("⚠️  Nessun messaggio trovato!")
            print()
            print("📝 ISTRUZIONI:")
            print("1. Apri Telegram e cerca: @allfoodsicilynotify_bot")
            print("2. Clicca su 'Start' o 'Avvia'")
            print("3. Invia un messaggio qualsiasi (es: 'Ciao')")
            print("4. Attendi 5 secondi")
            print("5. Esegui di nuovo questo script: python get_chat_id.py")
            print()
            sys.exit(1)
        
        # Estrai tutti i Chat ID unici
        chat_ids = set()
        for update in results:
            message = update.get("message", {})
            chat = message.get("chat", {})
            chat_id = chat.get("id")
            chat_type = chat.get("type", "unknown")
            
            if chat_id:
                chat_ids.add((chat_id, chat_type))
        
        if not chat_ids:
            print("⚠️  Nessun Chat ID trovato nei messaggi")
            sys.exit(1)
        
        print("✅ Chat ID trovato/i:")
        print()
        
        for chat_id, chat_type in chat_ids:
            print(f"   Chat ID: {chat_id}")
            print(f"   Tipo: {chat_type}")
            print()
            print(f"   Aggiungi al file .env:")
            print(f"   TELEGRAM_CHAT_ID={chat_id}")
            print()
        
        # Se c'è un solo Chat ID, suggerisci di copiarlo
        if len(chat_ids) == 1:
            chat_id = list(chat_ids)[0][0]
            print("💡 Copia questa riga nel tuo file .env:")
            print(f"TELEGRAM_CHAT_ID={chat_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione: {str(e)}")
        print("Verifica la tua connessione internet e riprova")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    get_chat_id()

