# Quick Start Guide - AllFoodSicily

## Setup Rapido

### 1. Ambiente Virtuale (già creato)

```bash
cd /Users/vincibusa/Desktop/automazione/allfoodsicily
source venv/bin/activate
```

### 2. Comandi Utili

**Usa sempre `python3` o attiva il venv:**
```bash
# Opzione 1: Attiva venv (consigliato)
source venv/bin/activate
python test_telegram.py

# Opzione 2: Usa python3 direttamente
python3 test_telegram.py
```

### 3. Test Telegram (già funzionante ✅)

```bash
source venv/bin/activate
python test_telegram.py
```

### 4. Prossimi Passi

1. **Gemini API Key**: Ottieni da [Google AI Studio](https://aistudio.google.com/apikey)
2. **Firecrawl API Key**: Ottieni da [Firecrawl.dev](https://firecrawl.dev)
3. **Google Docs**: Configura OAuth2 (vedi README.md)

Aggiungi le chiavi al file `.env` e poi puoi eseguire il workflow completo!

### 5. Eseguire il Workflow

```bash
source venv/bin/activate
python main.py --now  # Esecuzione immediata
# oppure
python main.py        # Modalità scheduler (ogni giorno alle 9:00)
```

