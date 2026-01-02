# Setup Google Docs - Service Account

## ✅ Service Account Configurato

Il file `service_account.json` è già stato creato nella root del progetto.

## Importante: Condividi la Cartella con il Service Account

Il service account ha un email: `automazione@mediten-rag.iam.gserviceaccount.com`

**Per salvare i documenti in una cartella Google Drive, devi:**

1. **Crea o apri la cartella** su Google Drive dove vuoi salvare i documenti
2. **Condividi la cartella** con l'email del service account:
   - Clicca destro sulla cartella → "Condividi"
   - Aggiungi: `automazione@mediten-rag.iam.gserviceaccount.com`
   - Assegna il ruolo: **"Editor"** (per poter creare file)
   - Clicca "Invia"

3. **Ottieni l'ID della cartella**:
   - Apri la cartella su Google Drive
   - L'URL sarà tipo: `https://drive.google.com/drive/folders/1ABC123xyz...`
   - L'ID è la parte dopo `/folders/` (es: `1ABC123xyz...`)

4. **Aggiungi l'ID al `.env`**:
   ```env
   GOOGLE_DOCS_FOLDER_ID=1ABC123xyz...
   ```

## Test della Configurazione

Dopo aver configurato, puoi testare con:

```bash
source venv/bin/activate
python -c "from services.google_docs import GoogleDocsService; print('Google Docs configurato!')"
```

## Note

- Il service account **non richiede autenticazione browser** (perfetto per automazioni)
- I documenti verranno creati nella cartella condivisa
- Se non specifichi `GOOGLE_DOCS_FOLDER_ID`, i documenti verranno creati nella root del Drive del service account

