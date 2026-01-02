# AllFoodSicily Workflow Automation

Workflow automatizzato in Python per il giornale AllFoodSicily che:
- Ricerca novità nel settore food in Sicilia
- Monitora giornali siciliani per ispirazione
- Genera bozze di articoli con AI (Gemini)
- Crea immagini con AI (Nano Banana Pro)
- Salva su Google Docs
- Notifica via Telegram

## Requisiti

- Python 3.10 o superiore
- API Keys per:
  - Google Gemini (Google AI Studio)
  - Firecrawl
  - Telegram Bot
  - Google Cloud (per Google Docs)

## Installazione

1. **Clona o naviga nella directory del progetto:**
   ```bash
   cd allfoodsicily
   ```

2. **Crea un ambiente virtuale:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente:**
   ```bash
   cp .env.example .env
   ```
   
   Modifica il file `.env` e inserisci le tue API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   GOOGLE_DOCS_FOLDER_ID=your_google_drive_folder_id_here
   ```

## Configurazione API

### Google Gemini API
1. Vai su [Google AI Studio](https://aistudio.google.com/apikey)
2. Crea una nuova API key
3. Copia la key nel file `.env`

### Firecrawl API
1. Vai su [Firecrawl](https://firecrawl.dev)
2. Crea un account e ottieni la tua API key
3. Copia la key nel file `.env`

### Telegram Bot
1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot` e segui le istruzioni
3. Salva il token fornito
4. Per ottenere il Chat ID:
   - Avvia una conversazione con il bot
   - Visita: `https://api.telegram.org/bot<IL_TUO_TOKEN>/getUpdates`
   - Cerca `"chat":{"id":` nel JSON - quel numero è il tuo Chat ID
5. Inserisci token e chat ID nel file `.env`

### Google Docs API
1. Vai su [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita le API:
   - Google Docs API
   - Google Drive API
4. Crea credenziali OAuth 2.0:
   - Tipo: Applicazione desktop
   - Scarica il file JSON
   - Rinomina in `credentials.json` e posizionalo nella root del progetto
5. La prima esecuzione aprirà il browser per l'autenticazione
6. Il token verrà salvato automaticamente in `token.json`

## Utilizzo

### Esecuzione Immediata
Per eseguire il workflow immediatamente:
```bash
python main.py --now
```

### Modalità Scheduler
Per eseguire il workflow automaticamente ogni giorno alle 9:00:
```bash
python main.py
```

### Validazione Configurazione
Per verificare che tutte le configurazioni siano corrette:
```bash
python main.py --validate
```

## Struttura del Progetto

```
allfoodsicily/
├── config/              # Configurazione
│   ├── settings.py      # Impostazioni e variabili ambiente
│   └── sources.py       # Siti da monitorare
├── services/            # Servizi esterni
│   ├── scraper.py       # Firecrawl integration
│   ├── gemini_client.py # Gemini API
│   ├── image_generator.py # Nano Banana Pro
│   ├── google_docs.py   # Google Docs API
│   └── telegram_bot.py # Telegram notifications
├── workflow/            # Fasi del workflow
│   ├── search_phase.py  # Fase 1: Ricerca
│   ├── scrape_phase.py  # Fase 2: Scraping
│   ├── analysis_phase.py # Fase 3: Analisi
│   ├── generation_phase.py # Fase 4: Generazione
│   └── output_phase.py  # Fase 5: Output
├── models/              # Modelli dati
│   └── schemas.py       # Pydantic schemas
├── utils/               # Utilities
│   ├── logger.py        # Logging
│   └── retry.py         # Retry logic
├── main.py              # Entry point
└── requirements.txt    # Dipendenze
```

## Flusso di Esecuzione

1. **Fase 1 - Ricerca**: Cerca novità food in Sicilia con Firecrawl Search
2. **Fase 2 - Scraping**: Scrapa 8 siti siciliani in parallelo
3. **Fase 3 - Analisi**: Gemini analizza i contenuti e seleziona 3-5 topic
4. **Fase 4 - Generazione**: 
   - Gemini genera articoli (500-800 parole)
   - Nano Banana Pro genera immagini (2K, 16:9)
5. **Fase 5 - Output**:
   - Salva articoli su Google Docs
   - Invia notifica Telegram con riepilogo

## Siti Monitorati

### Giornali Generalisti
- Giornale di Sicilia (gds.it/food)
- LiveSicilia (livesicilia.it/food-beverage)
- Balarm (balarm.it/food)
- BlogSicilia (blogsicilia.it)

### Siti Specializzati
- Cronache di Gusto (cronachedigusto.it)
- Sicilia da Gustare (siciliadagustare.com)
- Culture & Terroir (cultureandterroir.com/food)
- Sapori e Saperi di Sicilia (saporiesaperidisicilia.it/notizie)

## Costi Stimati

| Servizio | Utilizzo | Costo/Esecuzione |
|----------|----------|------------------|
| Gemini Flash | ~20K tokens | ~$0.02 |
| Nano Banana Pro | 5 immagini 2K | ~$0.10 |
| Firecrawl | ~10 scrapes | ~$0.05 |
| **Totale giornaliero** | | **~$0.17** |
| **Totale mensile** | | **~$5.10** |

## Logging

I log vengono salvati in:
- Console: Output in tempo reale
- File: `logs/workflow.log` (log dettagliati)

## Troubleshooting

### Errori di Autenticazione Google
- Assicurati che `credentials.json` sia presente
- La prima esecuzione aprirà il browser per l'autenticazione
- Verifica che le API siano abilitate nel Google Cloud Console

### Errori Firecrawl
- Verifica che la tua API key sia valida
- Controlla i limiti del tuo piano Firecrawl

### Errori Telegram
- Verifica che il bot token sia corretto
- Assicurati che il Chat ID sia valido
- Se usi un gruppo, il bot deve essere admin

### Nessun Topic Selezionato
- Verifica che ci siano contenuti recenti nei siti monitorati
- Controlla i log per vedere se lo scraping ha funzionato

## Sviluppo

Per contribuire o modificare il workflow:

1. I prompt AI sono in `services/gemini_client.py`
2. I siti monitorati sono in `config/sources.py`
3. Le impostazioni sono in `config/settings.py`

## Licenza

Questo progetto è per uso interno di AllFoodSicily.

