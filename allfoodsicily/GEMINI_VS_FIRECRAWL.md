# Gemini Search vs Firecrawl - Confronto

## Opzioni Disponibili

Hai due opzioni per la ricerca e scraping:

### Opzione 1: Gemini con Google Search (CONSIGLIATO) ✅

**Vantaggi:**
- ✅ **Nessun costo aggiuntivo** - Usa solo Gemini API
- ✅ **Ricerca intelligente** - Google Search integrato
- ✅ **Meno dipendenze** - Non serve Firecrawl
- ✅ **Gemini 3 Flash** supporta Google Search grounding nativamente

**Configurazione:**
```env
USE_GEMINI_SEARCH=true
GEMINI_TEXT_MODEL=gemini-3-flash-preview
```

**Come funziona:**
- Gemini usa Google Search per trovare notizie recenti
- Restituisce URL, titoli e snippet
- Per lo scraping dei siti, usa ancora Firecrawl (o puoi usare Gemini URL context)

### Opzione 2: Firecrawl (Tradizionale)

**Vantaggi:**
- ✅ Scraping più affidabile per siti complessi
- ✅ Supporto per screenshot, links, etc.

**Svantaggi:**
- ❌ Costo aggiuntivo (~$0.05 per esecuzione)
- ❌ Richiede API key separata

**Configurazione:**
```env
USE_GEMINI_SEARCH=false
FIRECRAWL_API_KEY=your_key_here
```

## Modello Gemini Corretto

**IMPORTANTE**: Il modello corretto è:
- ✅ `gemini-3-flash-preview` (corretto)
- ❌ `gemini-3.0-flash-preview` (NON esiste)

## Raccomandazione

**Usa Gemini Search** (`USE_GEMINI_SEARCH=true`) perché:
1. Risparmi su Firecrawl
2. Gemini 3 Flash è ottimizzato per ricerca web
3. Meno configurazione necessaria
4. Integrazione più semplice

Per lo scraping dei siti specifici, puoi ancora usare Firecrawl se necessario, oppure usare Gemini con URL context.

