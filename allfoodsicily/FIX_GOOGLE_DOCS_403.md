# Risoluzione Errore Google Docs 403

## Problema
```
HttpError 403: The caller does not have permission
```

## Soluzione

### 1. Condividi la Cartella Google Drive con il Service Account

Il Service Account ha email: **`automazione@mediten-rag.iam.gserviceaccount.com`**

**Passi da seguire:**

1. **Apri Google Drive** e vai alla cartella dove vuoi salvare i documenti
   - ID cartella: `1F5plbErfnxjWsqnHPF-a-3IemT2qkbgk`
   - URL: `https://drive.google.com/drive/folders/1F5plbErfnxjWsqnHPF-a-3IemT2qkbgk`

2. **Condividi la cartella** con il Service Account:
   - Clicca destro sulla cartella → **"Condividi"** (o icona "Condividi")
   - Nel campo "Aggiungi persone e gruppi", inserisci:
     ```
     automazione@mediten-rag.iam.gserviceaccount.com
     ```
   - Assegna il ruolo: **"Editor"** (per poter creare file)
   - **IMPORTANTE**: Rimuovi il flag "Notifica alle persone" (non serve)
   - Clicca **"Invia"** o **"Condividi"**

3. **Verifica i permessi**:
   - La cartella deve essere visibile al Service Account
   - Il Service Account deve avere ruolo "Editor" o "Proprietario"

### 2. Verifica l'ID della Cartella nel .env

L'ID della cartella nel `.env` è stato pulito. Verifica che sia corretto:

```env
GOOGLE_DOCS_FOLDER_ID=1F5plbErfnxjWsqnHPF-a-3IemT2qkbgk
```

**IMPORTANTE**: L'ID deve essere solo la parte dopo `/folders/` nell'URL, senza parametri aggiuntivi.

### 3. Test della Configurazione

Dopo aver condiviso la cartella, testa:

```bash
cd /Users/vincibusa/Desktop/automazione/allfoodsicily
source venv/bin/activate
python -c "from services.google_docs import GoogleDocsService; s = GoogleDocsService(); print('✅ Google Docs configurato correttamente!')"
```

### 4. Se l'Errore Persiste

Se dopo aver condiviso la cartella l'errore persiste:

1. **Verifica che il Service Account abbia i permessi API attivati**:
   - Vai a [Google Cloud Console](https://console.cloud.google.com/)
   - Progetto: `mediten-rag`
   - API & Services → Enabled APIs
   - Verifica che siano attivate:
     - Google Docs API
     - Google Drive API

2. **Verifica che il Service Account esista**:
   - IAM & Admin → Service Accounts
   - Cerca: `automazione@mediten-rag.iam.gserviceaccount.com`
   - Deve essere presente e attivo

3. **Prova a creare un documento senza cartella**:
   - Rimuovi temporaneamente `GOOGLE_DOCS_FOLDER_ID` dal `.env`
   - I documenti verranno creati nella root del Drive del Service Account
   - Se funziona, il problema è solo la condivisione della cartella

## Note

- Il Service Account **non può accedere a cartelle private** senza essere condiviso
- La condivisione deve essere fatta **manualmente** su Google Drive
- Una volta condivisa, la cartella rimane accessibile al Service Account finché non rimuovi i permessi

