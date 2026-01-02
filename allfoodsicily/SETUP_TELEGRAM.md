# Setup Telegram Bot - Guida Rapida

## Token Bot (già ottenuto)
Il tuo token è: `8561234151:AAHZ7xFRfF1hUWJyRZkxTZRWcjDUm9MvOGE`

## Come ottenere il Chat ID

### Metodo 1: Chat Privata (consigliato per test)

1. **Apri Telegram** e cerca il tuo bot: `@allfoodsicilynotify_bot`
2. **Avvia una conversazione** con il bot:
   - Clicca su "Start" o "Avvia"
   - **OPPURE** invia un messaggio qualsiasi (es: "Ciao" o "/start")
3. **IMPORTANTE**: Aspetta qualche secondo dopo aver inviato il messaggio
4. **Apri nel browser** questo URL:
   ```
   https://api.telegram.org/bot8561234151:AAHZ7xFRfF1hUWJyRZkxTZRWcjDUm9MvOGE/getUpdates
   ```
5. **Se vedi `"result":[]`** significa che non ci sono messaggi ancora:
   - Torna su Telegram e assicurati di aver inviato un messaggio al bot
   - Attendi 5-10 secondi
   - Ricarica la pagina del browser (F5)
6. **Cerca nel JSON** la riga che contiene `"chat":{"id":`
7. **Il numero dopo `"id":` è il tuo Chat ID** (es: `123456789`)

### Metodo 2: Gruppo Telegram

Se vuoi ricevere notifiche in un gruppo:

1. **Crea o apri un gruppo** su Telegram
2. **Aggiungi il bot al gruppo** (cerca `@allfoodsicilynotify_bot`)
3. **Rendi il bot admin** (opzionale ma consigliato)
4. **Invia un messaggio nel gruppo** (puoi scrivere qualsiasi cosa)
5. **Apri nel browser** lo stesso URL di prima:
   ```
   https://api.telegram.org/bot8561234151:AAHZ7xFRfF1hUWJyRZkxTZRWcjDUm9MvOGE/getUpdates
   ```
6. **Cerca `"chat":{"id":`** - il Chat ID del gruppo sarà un numero negativo (es: `-123456789`)

## Esempio di risposta JSON

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,
          "is_bot": false,
          "first_name": "Il Tuo Nome"
        },
        "chat": {
          "id": 987654321,  <-- QUESTO È IL TUO CHAT ID
          "first_name": "Il Tuo Nome",
          "type": "private"
        },
        "date": 1234567890,
        "text": "/start"
      }
    }
  ]
}
```

## Configurazione nel .env

Una volta ottenuto il Chat ID, aggiungi al file `.env`:

```env
TELEGRAM_BOT_TOKEN=8561234151:AAHZ7xFRfF1hUWJyRZkxTZRWcjDUm9MvOGE
TELEGRAM_CHAT_ID=987654321
```

## Test del Bot

Per testare che tutto funzioni:

```bash
python -c "from services.telegram_bot import TelegramNotifier; TelegramNotifier().send_notification('Test messaggio!')"
```

Se ricevi il messaggio su Telegram, la configurazione è corretta!

