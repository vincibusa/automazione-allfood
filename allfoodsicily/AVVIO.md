# 🚀 Guida Avvio AllFoodSicily Workflow

## Quick Start

### 1. Attiva l'ambiente virtuale

```bash
cd /Users/vincibusa/Desktop/automazione/allfoodsicily
source venv/bin/activate
```

### 2. Testa tutte le configurazioni

```bash
python test_all_services.py
```

Questo script verifica che tutte le API siano configurate correttamente.

### 3. Test singoli servizi (opzionale)

**Test Telegram:**
```bash
python test_telegram.py
```

**Test Google Docs:**
```bash
python -c "from services.google_docs import GoogleDocsService; print('✅ OK')"
```

### 4. Esegui il workflow

#### Opzione A: Esecuzione Immediata (consigliato per test)

```bash
python main.py --now
```

Questo esegue il workflow completo una volta:
- Cerca novità food in Sicilia
- Scrapa i siti monitorati
- Analizza e seleziona topic
- Genera articoli e immagini
- Salva su Google Docs
- Invia notifica Telegram

#### Opzione B: Modalità Scheduler (produzione)

```bash
python main.py
```

Esegue il workflow automaticamente ogni giorno alle 9:00 (configurabile nel `.env`).

Per fermare: `Ctrl+C`

## Struttura Esecuzione

Il workflow esegue 5 fasi sequenziali:

1. **Fase 1 - Ricerca**: Cerca novità food con Firecrawl Search
2. **Fase 2 - Scraping**: Scrapa 8 siti siciliani in parallelo
3. **Fase 3 - Analisi**: Gemini seleziona 3-5 topic interessanti
4. **Fase 4 - Generazione**: 
   - Gemini genera articoli (500-800 parole)
   - Nano Banana Pro genera immagini (2K, 16:9)
5. **Fase 5 - Output**:
   - Salva articoli su Google Docs
   - Invia notifica Telegram

## Log e Debug

I log vengono salvati in:
- **Console**: Output in tempo reale
- **File**: `logs/workflow.log` (log dettagliati)

Per vedere più dettagli, attiva il debug mode nel `.env`:
```env
DEBUG_MODE=true
```

## Troubleshooting

### Errore "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Errore Google Docs
- Verifica che `service_account.json` esista
- Verifica che la cartella Drive sia condivisa con il service account
- Controlla che le API siano abilitate nel Google Cloud Console

### Errore Telegram
```bash
python test_telegram.py
```

### Errore Gemini/Firecrawl
- Verifica le API keys nel file `.env`
- Controlla i limiti del tuo piano

## Comandi Utili

```bash
# Validazione configurazione
python main.py --validate

# Test completo
python test_all_services.py

# Esecuzione immediata
python main.py --now

# Scheduler (background)
python main.py
```

## Prossimi Passi

Dopo il primo avvio riuscito:
1. Controlla i Google Docs creati
2. Verifica la notifica Telegram
3. Regola i prompt AI se necessario (in `services/gemini_client.py`)
4. Configura lo scheduler per esecuzione automatica

