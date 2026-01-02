# Setup Bot Telegram Interattivo - AllFoodSicily

## Modifiche Completate ✅

Il progetto è stato trasformato da workflow automatico con output Google Docs a **bot Telegram interattivo** con output PDF.

### Nuove Funzionalità

1. **Bot Interattivo**
   - Riceve comandi via Telegram
   - Riconosce linguaggio naturale
   - Genera articoli su richiesta

2. **Output PDF**
   - Gli articoli vengono inviati come PDF via Telegram
   - Include: testo + immagine + fonti
   - Google Docs è stato completamente rimosso

3. **Workflow Automatico Mantenuto**
   - Continua a girare alle 9:00 ogni giorno
   - Output su PDF invece di Google Docs

---

## Installazione

### 1. Installa le Nuove Dipendenze

```bash
cd allfoodsicily
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

Le nuove dipendenze installate sono:
- `fpdf2>=2.7.0` - Generazione PDF
- `pytz>=2024.1` - Gestione timezone per scheduler

### 2. Verifica Configurazione

Il bot non richiede più configurazioni Google Docs. Verifica solo:

```bash
python main.py --validate
```

Assicurati che nel tuo `.env` ci siano:
```env
GEMINI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

## Come Usare il Bot

### Modalità 1: Bot Interattivo con Scheduler (Consigliato)

Avvia il bot che rimane in ascolto **e** esegue il workflow alle 9:00:

```bash
python main.py
```

Il bot:
- ✅ Ascolta comandi e messaggi su Telegram
- ✅ Esegue workflow automatico alle 9:00
- ✅ Rimane attivo finché non lo fermi (Ctrl+C)

### Modalità 2: Workflow Immediato (Una Volta)

Esegui il workflow subito e termina:

```bash
python main.py --now
```

---

## Comandi Telegram

### Comandi Espliciti

```
/start          Messaggio di benvenuto
/help           Mostra aiuto
/articolo <topic>  Genera articolo su un topic
```

**Esempi:**
```
/articolo arancini siciliani
/articolo cannoli di Piana degli Albanesi
/articolo pistacchi di Bronte
```

### Linguaggio Naturale

Il bot capisce richieste in italiano:

```
"Scrivi un articolo sulla cassata siciliana"
"Fammi un pezzo sui cannoli"
"Vorrei un articolo sul Marsala"
"Genera un articolo sulle granite messinesi"
```

---

## Come Funziona

1. **Richiesta Utente** (Telegram)
   - Invii un comando o messaggio

2. **Bot Ricerca** (1-2 minuti)
   - Cerca informazioni con Gemini Search
   - Genera articolo con Gemini
   - Crea immagine con Gemini Image
   - Genera PDF

3. **Risposta**
   - Ricevi PDF completo su Telegram
   - Include testo + immagine + fonti

---

## Workflow Automatico (9:00)

Ogni mattina alle 9:00 (Europe/Rome):

1. Ricerca novità food Sicilia
2. Scrape 8 siti siciliani
3. Analizza e seleziona 3-5 topic
4. Genera articoli + immagini
5. **Invia PDF su Telegram** (non più Google Docs)

---

## Test del Bot

### Test 1: Validazione

```bash
python main.py --validate
```

Output atteso:
```
✅ Settings validation passed
```

### Test 2: Avvio Bot

```bash
python main.py
```

Output atteso:
```
🤖 Starting AllFoodSicily Bot with Scheduler
✅ Telegram Application built with handlers
✅ Scheduled daily workflow at 09:00 (Europe/Rome)
🎯 Bot is now ready!
```

### Test 3: Comando Telegram

Su Telegram, invia:
```
/start
```

Dovresti ricevere il messaggio di benvenuto.

### Test 4: Richiesta Articolo

Su Telegram, invia:
```
/articolo arancini di Catania
```

oppure

```
Scrivi un articolo sugli arancini
```

Dovresti ricevere:
1. Messaggio "🔄 Sto lavorando..."
2. Dopo 1-2 minuti: PDF completo dell'articolo

---

## Troubleshooting

### Il bot non risponde

- Verifica che `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` siano corretti nel `.env`
- Controlla i log: il bot stampa tutto su console
- Prova `/start` - dovrebbe sempre rispondere

### PDF non arrivano

- Controlla i log per errori durante la generazione PDF
- Verifica che `fpdf2` sia installato: `pip show fpdf2`

### Scheduler non parte alle 9:00

- Il timezone è impostato su `Europe/Rome` in `config/settings.py`
- Puoi cambiarlo nel `.env`: `TIMEZONE=Europe/Rome`
- Verifica che il bot sia in esecuzione all'orario schedulato

### Errore "Module not found"

Reinstalla le dipendenze:
```bash
pip install --upgrade -r requirements.txt
```

---

## File Modificati

### Nuovi File
- `services/pdf_generator.py` - Generatore PDF
- `workflow/manual_workflow.py` - Workflow per richieste manuali
- `SETUP_BOT.md` - Questo file

### File Modificati
- `services/telegram_bot.py` - Trasformato in bot interattivo
- `main.py` - Entry point con asyncio + scheduler
- `workflow/output_phase.py` - Output PDF invece di Google Docs
- `config/settings.py` - Rimosso Google Docs, aggiunto TIMEZONE
- `requirements.txt` - Aggiunto fpdf2, pytz

### File Rimossi
- `services/google_docs.py` - Non più necessario

---

## Prossimi Passi

1. **Testa il bot** con alcuni comandi
2. **Lascia girare** per vedere il workflow automatico domani alle 9:00
3. **Personalizza** i pattern di linguaggio naturale in `services/telegram_bot.py` se vuoi

Buon utilizzo! 🍝
